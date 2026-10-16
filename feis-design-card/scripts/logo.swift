// logo.swift —— 把浅底 LOGO 图处理成「白底 + 按内容裁切」的干净 PNG
//
// 用法: logo <in> <out> [inLow] [inHigh] [pad] [ex ey ew eh] [cx cy cw ch]
// 参数（可选）：
//   inLow/inHigh  电平映射区间，默认 0.34 / 0.86；小于 inLow 压成纯黑，大于 inHigh 提成纯白
//   pad           裁切时四周留白像素，默认 0
//   ex ey ew eh   在求外接框之前，先把这块矩形抹成白色（源图视觉坐标），用来去掉 LOGO 上的副文字
//
// 输出：白底 PNG（卡片底色为白，无需透明通道），已按内容外接框裁切。
// 编译: swiftc -O -swift-version 5 logo.swift -o logo
import Cocoa

let a = CommandLine.arguments
guard a.count >= 3 else {
    FileHandle.standardError.write("usage: logo <in> <out> [inLow] [inHigh] [pad] [ex ey ew eh]\n".data(using: .utf8)!)
    exit(2)
}
let inPath = a[1], outPath = a[2]
let inLow = a.count > 3 ? Double(a[3])! : 0.34
let inHigh = a.count > 4 ? Double(a[4])! : 0.86
let pad = a.count > 5 ? Int(a[5])! : 0

guard let img = NSImage(contentsOfFile: inPath) else {
    print("LOAD_FAIL"); exit(3)
}
var rect = CGRect.zero
guard let cg = img.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
    print("CG_FAIL"); exit(3)
}
let w = cg.width, h = cg.height

guard let ctx = CGContext(
    data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w * 4,
    space: CGColorSpace(name: CGColorSpace.sRGB)!,
    bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue)
) else { print("CTX_FAIL"); exit(4) }
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
guard let raw = ctx.data else { print("DATA_FAIL"); exit(4) }
let p = raw.bindMemory(to: UInt8.self, capacity: w * h * 4)

// 1) 电平映射：浅底(宣纸/米白) → 纯白，笔画 → 近黑
let span = max(inHigh - inLow, 0.001)
for i in stride(from: 0, to: w * h * 4, by: 4) {
    let lum = (0.2126 * Double(p[i]) + 0.7152 * Double(p[i + 1]) + 0.0722 * Double(p[i + 2])) / 255.0
    var t = (lum - inLow) / span
    t = min(max(t, 0), 1)
    let v = UInt8(255.0 * t)
    p[i] = v; p[i + 1] = v; p[i + 2] = v; p[i + 3] = 255
}

// 2) 抹掉指定矩形（坐标与后面的外接框同一套：位图行序 == 视觉行序，左上为原点）
if a.count > 8 {
    let ex = Int(a[6])!, ey = Int(a[7])!, ew = Int(a[8])!, eh = Int(a[9])!
    for y in max(ey, 0)..<min(ey + eh, h) {
        for x in max(ex, 0)..<min(ex + ew, w) {
            let i = (y * w + x) * 4
            p[i] = 255; p[i + 1] = 255; p[i + 2] = 255; p[i + 3] = 255
        }
    }
}

// 3) 求内容外接框（阈值 150）
var minX = w, minY = h, maxX = -1, maxY = -1
let cut: UInt8 = 150
for y in 0..<h {
    for x in 0..<w {
        if p[(y * w + x) * 4] < cut {
            if x < minX { minX = x }
            if x > maxX { maxX = x }
            if y < minY { minY = y }
            if y > maxY { maxY = y }
        }
    }
}
if maxX < 0 { print("EMPTY"); exit(5) }

// 4) 取图：给了 crop 参数就用它，否则用内容外接框
var bx = max(minX - pad, 0)
var by = max(minY - pad, 0)
var bw = min(maxX + pad, w - 1) - bx + 1
var bh = min(maxY + pad, h - 1) - by + 1

if a.count > 13 {
    bx = max(Int(a[10])!, 0); by = max(Int(a[11])!, 0)
    bw = min(Int(a[12])!, w - bx); bh = min(Int(a[13])!, h - by)
}

print("BBOX x=\(bx) y=\(by) w=\(bw) h=\(bh)  (source \(w)x\(h))  [左上为原点]")

guard let full = ctx.makeImage() else { print("IMG_FAIL"); exit(4) }
guard let crop = full.cropping(to: CGRect(x: bx, y: by, width: bw, height: bh)) else {
    print("CROP_FAIL"); exit(4)
}
guard let outCtx = CGContext(
    data: nil, width: bw, height: bh, bitsPerComponent: 8, bytesPerRow: bw * 4,
    space: CGColorSpace(name: CGColorSpace.sRGB)!,
    bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue)
) else { print("CTX2_FAIL"); exit(4) }
outCtx.setFillColor(CGColor(gray: 1, alpha: 1))
outCtx.fill(CGRect(x: 0, y: 0, width: bw, height: bh))
outCtx.draw(crop, in: CGRect(x: 0, y: 0, width: bw, height: bh))
guard let outCG = outCtx.makeImage() else { print("IMG2_FAIL"); exit(4) }
let rep = NSBitmapImageRep(cgImage: outCG)
guard let png = rep.representation(using: .png, properties: [:]) else {
    print("PNG_FAIL"); exit(4)
}
do {
    try png.write(to: URL(fileURLWithPath: outPath))
    print("OK -> \(outPath) \(bw)x\(bh)")
} catch {
    print("WRITE_FAIL \(error.localizedDescription)"); exit(3)
}
