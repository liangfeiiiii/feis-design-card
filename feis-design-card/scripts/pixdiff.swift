// 像素比对：判断两张 PNG 是否"画面完全一致"（不比对文件字节）。
// 用法: pixdiff <a.png> <b.png> [容差=0]
// 输出：不同的像素数、占比、最大通道差；退出码 0 = 画面一致，1 = 有差异。
import Cocoa

let a = CommandLine.arguments
guard a.count >= 3 else {
    FileHandle.standardError.write("usage: pixdiff <a.png> <b.png> [tol]\n".data(using: .utf8)!)
    exit(2)
}
let tol = a.count > 3 ? Int(a[3])! : 0

func load(_ p: String) -> (w: Int, h: Int, px: [UInt8])? {
    guard let img = NSImage(contentsOfFile: p),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    let w = cg.width, h = cg.height
    var buf = [UInt8](repeating: 0, count: w * h * 4)
    guard let ctx = CGContext(data: &buf, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: w * 4, space: CGColorSpaceCreateDeviceRGB(),
                              bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return nil }
    ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
    // 统一成非预乘，避免 alpha 干扰
    for i in stride(from: 0, to: buf.count, by: 4) {
        let al = Int(buf[i + 3])
        if al > 0 && al < 255 {
            buf[i]     = UInt8(min(255, Int(buf[i])     * 255 / al))
            buf[i + 1] = UInt8(min(255, Int(buf[i + 1]) * 255 / al))
            buf[i + 2] = UInt8(min(255, Int(buf[i + 2]) * 255 / al))
        }
    }
    return (w, h, buf)
}

guard let A = load(a[1]), let B = load(a[2]) else { print("cannot read"); exit(1) }
guard A.w == B.w && A.h == B.h else {
    print("尺寸不同: \(A.w)x\(A.h) vs \(B.w)x\(B.h)"); exit(1)
}

var diffPixels = 0
var maxDelta = 0
var sumDelta = 0
var worstX = -1, worstY = -1
let w = A.w, h = A.h
for y in 0..<h {
    for x in 0..<w {
        let i = (y * w + x) * 4
        var d = 0
        for c in 0..<3 {
            let dd = abs(Int(A.px[i + c]) - Int(B.px[i + c]))
            if dd > d { d = dd }
            if dd > maxDelta { maxDelta = dd }
        }
        if d > tol {
            diffPixels += 1
            sumDelta += d
            if d == maxDelta { worstX = x; worstY = y }
        }
    }
}
let total = w * h
let pct = 100.0 * Double(diffPixels) / Double(total)
print(String(format: "尺寸 %dx%d  不同像素 %d / %d  (%.4f%%)  最大通道差 %d  平均差 %.2f",
             w, h, diffPixels, total, pct, maxDelta,
             diffPixels > 0 ? Double(sumDelta) / Double(diffPixels) : 0.0))
if diffPixels > 0 { print("最差点坐标 (\(worstX), \(worstY))") }
exit(diffPixels == 0 ? 0 : 1)
