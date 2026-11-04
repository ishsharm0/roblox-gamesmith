# Open Cloud assets

Uploading needs your own Open Cloud API key with asset read/write permission, created at
https://create.roblox.com/dashboard/credentials. Save it as `~/.config/roblox/open-cloud.key` (mode 0600) and your creator in `~/.config/roblox/creator.json`
(`{"userId": 123}` or `{"groupId": 456}`).
`ROBLOX_OPEN_CLOUD_KEY` or `ROBLOX_OPEN_CLOUD_KEY_FILE` can override the private file.
Never paste the key into commands, game code, skill files or repository config.

```
rbxcloud info
rbxcloud upload model.glb --name "Original prop" --description "Authorship and license"
rbxcloud upload model.glb --name "Original prop" --upload --wait --out asset-operation.json
rbxcloud operation operations/<operation-id>
rbxcloud get <asset-id>
studio --studio <project-window> call insert_asset '{"assetId":"<asset-id>","assetName":"Original prop","assetType":"Model"}'
```

The first upload command previews the exact manifest and sends nothing. Upload is explicit; the
manifest always sets expectedPrice=0. Files must be nonempty and at most 20 MB. Supported formats
include GLB, glTF, FBX, RBXM/RBXMX, audio and images. Use self-contained GLB for textured models.
A timeout after creation is not permission to create another asset: keep the operation JSON and
poll its operation path. A successful upload may still await moderation; check the operation and
asset state before relying on it. Grant universe access for restricted audio/images when required.
A published-experience/universe ID is needed for that grant; an unpublished local place has none.

Asset permissions are separate from experience publishing permissions. A key with asset write does
not authorize or enable publishing a game. Respect authorization already supplied in the session;
ask only for a new action that needs authorization, after its exact content is ready to review.

Verified end to end while building Lily Pad Leap: key introspection, export -> RBXM upload ->
approved asset -> metadata read -> insertion in Studio. No Robux was spent.

Primary docs:
- https://create.roblox.com/docs/cloud/auth/api-keys#introspect-api-keys
- https://create.roblox.com/docs/cloud/guides/usage-assets
