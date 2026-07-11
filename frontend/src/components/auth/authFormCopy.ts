export type AuthMode = 'login' | 'register'
export type LoginMethod = 'password' | 'code'

export function getAccountLabel(mode: AuthMode, loginMethod: LoginMethod) {
  return mode === 'login' && loginMethod === 'password' ? '手机号 / 管理员账号' : '手机号'
}

export function getAccountPlaceholder(_mode: AuthMode, _loginMethod: LoginMethod) {
  return '13800000000'
}
