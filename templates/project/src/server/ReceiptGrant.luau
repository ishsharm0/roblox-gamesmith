-- Optional durable-product primitive; this game has no enabled paid products.
-- applyData must be a non-yielding function that changes ONLY the supplied data table.
local ReceiptGrant = {}
local busy = setmetatable({}, { __mode = "k" })
local function copy(value)
	if type(value) ~= "table" then
		return value
	end
	local result = {}
	for k, v in value do
		result[k] = copy(v)
	end
	return result
end
function ReceiptGrant.Grant(profile, purchaseId, applyData, timeout)
	if not profile or not profile:IsActive() or type(purchaseId) ~= "string" then
		return false
	end
	local saved = profile.LastSavedData.Receipts
	if saved and saved[purchaseId] then
		return true
	end
	if busy[profile] then
		return false
	end
	busy[profile] = true
	local ok, confirmed = pcall(function()
		local receipts = profile.Data.Receipts or {}
		if not receipts[purchaseId] then
			local staged = copy(profile.Data)
			staged.Receipts = staged.Receipts or {}
			applyData(staged)
			if not profile:IsActive() then
				return false
			end
			staged.Receipts[purchaseId] = true
			profile.Data = staged
		end
		profile:Save()
		local deadline = os.clock() + (timeout or 10)
		repeat
			local durable = profile.LastSavedData.Receipts
			if durable and durable[purchaseId] then
				return true
			end
			if not profile:IsActive() then
				return false
			end
			task.wait(0.05)
		until os.clock() >= deadline
		return false
	end)
	busy[profile] = nil
	return ok and confirmed == true
end
return ReceiptGrant
