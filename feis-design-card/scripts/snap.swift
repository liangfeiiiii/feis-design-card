// article-to-card 截图器：WKWebView 离屏渲染 HTML → PNG
// 用法: snap <in.html> <out.png> <width> <height>
// 编译: swiftc -O -swift-version 5 snap.swift -o snap
import Cocoa
import WebKit

final class Coord: NSObject, WKNavigationDelegate {
    let out: String
    let w: CGFloat
    let h: CGFloat

    init(out: String, w: CGFloat, h: CGFloat) {
        self.out = out
        self.w = w
        self.h = h
    }

    // 把快照规格化为严格的 w×h @1x PNG（防止 Retina 2x 输出）
    func normalize(_ img: NSImage) -> Data? {
        guard let ctx = CGContext(
            data: nil, width: Int(w), height: Int(h),
            bitsPerComponent: 8, bytesPerRow: Int(w) * 4,
            space: CGColorSpace(name: CGColorSpace.sRGB),
            bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue)
        ) else { return nil }
        ctx.setFillColor(CGColor(gray: 0.949, alpha: 1))
        ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
        var rect = CGRect(x: 0, y: 0, width: w, height: h)
        guard let cg = img.cgImage(forProposedRect: &rect, context: nil, hints: nil) else { return nil }
        ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
        guard let outCG = ctx.makeImage() else { return nil }
        return NSBitmapImageRep(cgImage: outCG).representation(
            using: NSBitmapImageRep.FileType.png, properties: [:]
        )
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // 等待字体加载与布局稳定
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { [weak self] in
            guard let self = self else { return }
            let config = WKSnapshotConfiguration()
            config.rect = CGRect(x: 0, y: 0, width: self.w, height: self.h)
            webView.takeSnapshot(with: config) { image, error in
                guard let img = image else {
                    print("SNAP_FAIL \(error?.localizedDescription ?? "unknown")")
                    exit(4)
                }
                guard let png = self.normalize(img) else {
                    print("SNAP_FAIL normalize")
                    exit(4)
                }
                do {
                    try png.write(to: URL(fileURLWithPath: self.out))
                    print("OK")
                    exit(0)
                } catch {
                    print("WRITE_FAIL \(error.localizedDescription)")
                    exit(3)
                }
            }
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("NAV_FAIL \(error.localizedDescription)")
        exit(5)
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        print("NAV_FAIL \(error.localizedDescription)")
        exit(5)
    }
}

let a = CommandLine.arguments
guard a.count >= 5 else {
    FileHandle.standardError.write("usage: snap <in.html> <out.png> <w> <h>\n".data(using: .utf8)!)
    exit(2)
}
let inURL = URL(fileURLWithPath: a[1]).standardizedFileURL
let outPath = a[2]
let w = CGFloat(Double(a[3])!)
let h = CGFloat(Double(a[4])!)

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)

let webView = WKWebView(frame: NSRect(x: 0, y: 0, width: w, height: h))
let coord = Coord(out: outPath, w: w, h: h)
webView.navigationDelegate = coord

// 读取权限放开到根目录：卡片引用的图片可能在任意位置（vault assets 等）
webView.loadFileURL(inURL, allowingReadAccessTo: URL(fileURLWithPath: "/"))

DispatchQueue.global().asyncAfter(deadline: .now() + 30) {
    print("TIMEOUT")
    exit(6)
}

app.run()
