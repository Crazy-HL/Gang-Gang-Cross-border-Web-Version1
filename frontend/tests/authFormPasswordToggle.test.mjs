import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'

const source = await readFile(path.resolve('src/components/auth/AuthForm.vue'), 'utf8')

assert.match(source, /lucide-vue-next/)
assert.match(source, /showPassword/)
assert.match(source, /:type="showPassword \? 'text' : 'password'"/)
assert.match(source, /watch\(\[mode, loginMethod\]/)
assert.match(source, /showPassword\.value = false/)
assert.match(source, /auth-password-input/)
assert.match(source, /::-ms-reveal/)
assert.match(source, /::-ms-clear/)
assert.match(source, /显示密码/)
assert.match(source, /隐藏密码/)
