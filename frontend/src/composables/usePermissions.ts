import { computed } from 'vue'
import { useAuthStore } from '../stores/authStore'

export function usePermissions() {
  const auth = useAuthStore()

  /**
   * 检查当前用户是否有权执行指定操作。
   * @param action 'read' | 'create' | 'edit' | 'delete'
   */
  const can = (action: 'read' | 'create' | 'edit' | 'delete'): boolean => {
    if (auth.user?.is_superuser) return true

    const profileType = auth.user?.profile_type
    if (!profileType) return action === 'read' // 无 profile 仅可读

    // admin: 全部操作
    if (profileType === 'admin') return true
    // standard: read/create/edit (无 delete)
    if (profileType === 'standard') return action !== 'delete'
    // readonly: 仅 read
    if (profileType === 'readonly') return action === 'read'

    return false
  }

  /**
   * 检查是否为管理员（拥有全部权限）
   */
  const isAdmin = computed(() => {
    return auth.user?.is_superuser || auth.user?.profile_type === 'admin'
  })

  /**
   * 检查是否可删除（Standard User 不可删除，Read Only 不可删除）
   */
  const canDelete = computed(() => can('delete'))

  return { can, canDelete, isAdmin }
}