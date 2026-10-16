// 行剖面：扫描一张卡片 PNG，输出「有墨的行」合并成的文字块，以及块间距。
// 用法: rowprofile <img.png> [ink阈值=235] [最少墨点数=2]
// 判据：某行若有 >= 最少墨点数的像素比阈值暗，就算有墨。
import Cocoa

let a = CommandLine.arguments
guard a.count >= 2 else {
    FileHandle.standardError.write("usage: rowprofile <img.png> [th] [minInk]\n".data(using: .utf8)!)
    exit(2)
}
let th = a.count > 2 ? Int(a[2])! : 235
let minInk = a.count > 3 ? Int(a[3])! : 2

guard let src = NSImage(contentsOfFile: a[1]),
      let cg = src.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("cannot read"); exit(1)
}
let w = cg.width, h = cg.height
var px = [UInt8](repeating: 0, count: w * h * 4)
let cs = CGColorSpaceCreateDeviceRGB()
guard let ctx = CGContext(data: &px, width: w, height: h, bitsPerComponent: 8,
                          bytesPerRow: w * 4, space: cs,
                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else {
    print("ctx fail"); exit(1)
}
ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))

// 逐行统计墨点数（位图行序 = 视觉行序）
var ink = [Int](repeating: 0, count: h)
for y in 0..<h {
    var c = 0
    for x in stride(from: 0, to: w, by: 2) {
        let i = (y * w + x) * 4
        let lum = (Int(px[i]) * 299 + Int(px[i+1]) * 587 + Int(px[i+2]) * 114) / 1000
        if lum < th { c += 1 }
    }
    ink[y] = c
}

// 合并成块
var blocks: [(Int, Int)] = []
var cur: Int? = nil
for y in 0..<h {
    if ink[y] >= minInk {
        if cur == nil { cur = y }
    } else if let s = cur {
        blocks.append((s, y - 1)); cur = nil
    }
}
if let s = cur { blocks.append((s, h - 1)) }

print("size \(w)x\(h)  阈值 \(th)")
print("序号 |  y 区间     | 高   | 与上一块的空隙")
var prevBottom: Int? = nil
for (i, b) in blocks.enumerated() {
    let gapStr: String
    if let p = prevBottom {
        gapStr = "\(b.0 - p - 1)px"
    } else {
        gapStr = "—"
    }
    let idx = String(format: "%3d", i + 1)
    let range = String(format: "%5d..%-5d", b.0, b.1)
    let hgt = String(format: "%4d", b.1 - b.0 + 1)
    print("\(idx)  | \(range) | \(hgt) | \(gapStr)")
    prevBottom = b.1
}
