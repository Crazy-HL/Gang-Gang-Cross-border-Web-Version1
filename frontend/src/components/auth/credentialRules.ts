export const ADMIN_LOGIN_ACCOUNT = 'admin'

const PHONE_NUMBER_PATTERN = /^1\d{10}$/

export function normalizeAccount(account: string) {
  return account.trim()
}

export function isPhoneNumber(account: string) {
  return PHONE_NUMBER_PATTERN.test(normalizeAccount(account))
}

export function isAdminLoginAccount(account: string) {
  return normalizeAccount(account) === ADMIN_LOGIN_ACCOUNT
}

export function canUsePasswordLoginAccount(account: string) {
  return isPhoneNumber(account) || isAdminLoginAccount(account)
}

export function canUseCodeAccount(account: string) {
  return isPhoneNumber(account)
}

export function canUseRegisterAccount(account: string) {
  return isPhoneNumber(account)
}
