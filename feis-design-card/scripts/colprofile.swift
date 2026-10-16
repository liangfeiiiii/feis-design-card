// 列剖面：扫描一张卡片 PNG 在**指定 y 区间**内的墨迹横向范围。
// 用法: colprofile <img.png> [y0=0] [y1=全高] [ink阈值=200]
// 输出：该区间内最左／最右墨点的 x、实际字宽，以及横向分段（字与字之间的空档）。
// 用途：判断「这行还能不能再大一号」——量出当前字串实占宽度，和版心宽一比就知道余量。
import Cocoa

let a = CommandLine.arguments
guard a.count >= 2 else {
    FileHandle.standardError.write("usage: colprofile <img.png> [y0] [y1] [th]\n".data(using: .utf8)!)
    exit(2)
}

guard let src = NSImage(contentsOfFile: a[1]),
      let cg = src.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("cannot read"); exit(1)
}
let w = cg.width, h = cg.height
let y0 = a.count > 2 ? max(0, min(h - 1, Int(a[2])!)) : 0
let y1 = a.count > 3 ? max(y0, min(h - 1, Int(a[3])!)) : h - 1
let th = a.count > 4 ? Int(a[4])! : 200

var px = [UInt8](repeating: 0, count: w * h * 4)
let cs = CGColorSpaceCreateDeviceRGB()
guard let ctx = CGContext(data: &px, width: w, height: h, bitsPerComponent: 8,
                          bytesPerRow: w * 4, space: cs,
                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else {
    print("ctx fail"); exit(1)
}
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))

var ink = [Int](repeating: 0, count: w)
for y in y0...y1 {
    for x in 0..<w {
        let i = (y * w + x) * 4
        let lum = (Int(px[i]) * 299 + Int(px[i + 1]) * 587 + Int(px[i + 2]) * 114) / 1000
        if lum < th { ink[x] += 1 }
    }
}

var minX = -1, maxX = -1
for x in 0..<w where ink[x] > 0 {
    if minX < 0 { minX = x }
    maxX = x
}
print("size \(w)x\(h)  y \(y0)..\(y1)  阈值 \(th)")
guard minX >= 0 else { print("该区间内没有墨迹"); exit(0) }
print(String(format: "墨迹 x %d..%d   宽 %d   左边距 %d   右边距 %d",
             minX, maxX, maxX - minX + 1, minX, w - 1 - maxX))

// 横向分段（连续有墨的列合并；空档 > 12px 才断开，避免把字内空隙切开）
var segs: [(Int, Int)] = []
var cur: Int? = nil
var blank = 0
for x in 0..<w {
    if ink[x] > 0 {
        if cur == nil { cur = x }
        blank = 0
    } else if let s = cur {
        blank += 1
        if blank > 12 { segs.append((s, x - blank)); cur = nil }
    }
}
if let s = cur { segs.append((s, maxX)) }
print("分段 \(segs.count) 个（空档 >12px 才算断）:")
for (i, sg) in segs.enumerated() where segs.count <= 40 {
    print(String(format: "  %2d | x %5d..%-5d | 宽 %4d", i + 1, sg.0, sg.1, sg.1 - sg.0 + 1))
}
