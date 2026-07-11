import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import ts from 'typescript'

const sourcePath = path.resolve('src/components/auth/credentialRules.ts')
const source = await readFile(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2020,
  },
})

const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString('base64')}`
const rules = await import(moduleUrl)

assert.equal(rules.isPhoneNumber('13800138000'), true)
assert.equal(rules.isPhoneNumber('admin'), false)

assert.equal(rules.canUsePasswordLoginAccount('13800138000'), true)
assert.equal(rules.canUsePasswordLoginAccount('admin'), true)
assert.equal(rules.canUsePasswordLoginAccount('Admin'), false)
assert.equal(rules.canUsePasswordLoginAccount('admin1'), false)
assert.equal(rules.canUsePasswordLoginAccount('testuser'), false)

assert.equal(rules.canUseCodeAccount('13800138000'), true)
assert.equal(rules.canUseCodeAccount('admin'), false)

assert.equal(rules.canUseRegisterAccount('13800138000'), true)
assert.equal(rules.canUseRegisterAccount('admin'), false)
