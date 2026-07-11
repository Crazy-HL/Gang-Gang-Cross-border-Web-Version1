import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import ts from 'typescript'

const sourcePath = path.resolve('src/api/apiBaseUrl.ts')
const source = await readFile(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2020,
  },
})

const moduleUrl = `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString('base64')}`
const { API_BASE_URL, normalizeApiBaseUrl } = await import(moduleUrl)

assert.equal(normalizeApiBaseUrl(undefined), '')
assert.equal(normalizeApiBaseUrl(''), '')
assert.equal(normalizeApiBaseUrl('https://api.example.com'), 'https://api.example.com')
assert.equal(API_BASE_URL, '')
