-- base64 for moving binary model files (rbxm) through execute_luau's text channel
local A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local ENC = buffer.create(64)
local DEC = table.create(256, -1)
for i = 1, 64 do
	buffer.writeu8(ENC, i - 1, string.byte(A, i))
	DEC[string.byte(A, i) + 1] = i - 1
end
local function encode(b: buffer): string
	local n = buffer.len(b)
	local out = buffer.create(math.ceil(n / 3) * 4)
	local o = 0
	for i = 0, n - 1, 3 do
		local b0 = buffer.readu8(b, i)
		local b1 = if i + 1 < n then buffer.readu8(b, i + 1) else 0
		local b2 = if i + 2 < n then buffer.readu8(b, i + 2) else 0
		local v = b0 * 65536 + b1 * 256 + b2
		buffer.writeu8(out, o, buffer.readu8(ENC, v // 262144))
		buffer.writeu8(out, o + 1, buffer.readu8(ENC, (v // 4096) % 64))
		buffer.writeu8(out, o + 2, if i + 1 < n then buffer.readu8(ENC, (v // 64) % 64) else 61)
		buffer.writeu8(out, o + 3, if i + 2 < n then buffer.readu8(ENC, v % 64) else 61)
		o += 4
	end
	return buffer.tostring(out)
end
local function decode(s: string): buffer
	s = s:gsub("[^%w%+/=]", "")
	local pad = select(2, s:gsub("=", ""))
	local n = #s // 4 * 3 - pad
	local out = buffer.create(n)
	local o = 0
	for i = 1, #s, 4 do
		local c0, c1, c2, c3 = string.byte(s, i, i + 3)
		local v = DEC[c0 + 1] * 262144 + DEC[c1 + 1] * 4096 + math.max(DEC[c2 + 1], 0) * 64 + math.max(DEC[c3 + 1], 0)
		if o < n then buffer.writeu8(out, o, v // 65536) end
		if o + 1 < n then buffer.writeu8(out, o + 1, (v // 256) % 256) end
		if o + 2 < n then buffer.writeu8(out, o + 2, v % 256) end
		o += 3
	end
	return out
end
