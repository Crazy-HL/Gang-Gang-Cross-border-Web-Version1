import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import ts from 'typescript'

const sourcePath = path.resolve('src/components/auth/authFormCopy.ts')
const source = await readFile(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2020,
  },
})

const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString('base64')}`
const { getAccountLabel, getAccountPlaceholder } = await import(moduleUrl)

assert.equal(getAccountLabel('login', 'password'), '手机号 / 管理员账号')
assert.equal(getAccountLabel('login', 'code'), '手机号')
assert.equal(getAccountLabel('register', 'password'), '手机号')

assert.equal(getAccountPlaceholder('login', 'password'), '13800000000')
assert.equal(getAccountPlaceholder('login', 'code'), '13800000000')
assert.equal(getAccountPlaceholder('register', 'password'), '13800000000')
assert.equal(getAccountPlaceholder('login', 'password').includes('admin'), false)
