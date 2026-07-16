import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/',
      component: () => import('../components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue'),
        },
        {
          path: 'accounts',
          name: 'AccountList',
          component: () => import('../views/accounts/AccountList.vue'),
        },
        {
          path: 'accounts/new',
          name: 'AccountCreate',
          component: () => import('../views/accounts/AccountForm.vue'),
        },
        {
          path: 'accounts/:id',
          name: 'AccountDetail',
          component: () => import('../views/accounts/AccountDetail.vue'),
        },
        {
          path: 'accounts/:id/edit',
          name: 'AccountEdit',
          component: () => import('../views/accounts/AccountForm.vue'),
        },
        {
          path: 'contacts',
          name: 'ContactList',
          component: () => import('../views/contacts/ContactList.vue'),
        },
        {
          path: 'contacts/new',
          name: 'ContactCreate',
          component: () => import('../views/contacts/ContactForm.vue'),
        },
        {
          path: 'contacts/:id',
          name: 'ContactDetail',
          component: () => import('../views/contacts/ContactDetail.vue'),
        },
        {
          path: 'contacts/:id/edit',
          name: 'ContactEdit',
          component: () => import('../views/contacts/ContactForm.vue'),
        },
        {
          path: 'products',
          name: 'ProductList',
          component: () => import('../views/products/ProductList.vue'),
        },
        {
          path: 'products/new',
          name: 'ProductCreate',
          component: () => import('../views/products/ProductForm.vue'),
        },
        {
          path: 'products/:id',
          name: 'ProductDetail',
          component: () => import('../views/products/ProductDetail.vue'),
        },
        {
          path: 'products/:id/edit',
          name: 'ProductEdit',
          component: () => import('../views/products/ProductForm.vue'),
        },
        {
          path: 'opportunities',
          name: 'OpportunityList',
          component: () => import('../views/opportunities/OpportunityList.vue'),
        },
        {
          path: 'opportunities/pipeline',
          name: 'PipelineBoard',
          component: () => import('../views/opportunities/PipelineBoard.vue'),
        },
        {
          path: 'opportunities/new',
          name: 'OpportunityCreate',
          component: () => import('../views/opportunities/OpportunityForm.vue'),
        },
        {
          path: 'opportunities/:id',
          name: 'OpportunityDetail',
          component: () => import('../views/opportunities/OpportunityDetail.vue'),
        },
        {
          path: 'opportunities/:id/edit',
          name: 'OpportunityEdit',
          component: () => import('../views/opportunities/OpportunityForm.vue'),
        },
        {
          path: 'admin/objects',
          name: 'ObjectList',
          component: () => import('../views/custom-objects/ObjectList.vue'),
        },
        {
          path: 'admin/objects/new',
          name: 'ObjectCreate',
          component: () => import('../views/custom-objects/ObjectDesigner.vue'),
        },
        {
          path: 'admin/objects/:id',
          name: 'ObjectDesigner',
          component: () => import('../views/custom-objects/ObjectDesigner.vue'),
        },
        {
          path: 'admin/objects/:id/records',
          name: 'ObjectRecords',
          component: () => import('../views/custom-objects/ObjectRecords.vue'),
        },
        {
          path: 'admin/objects/:id/records/:record_id',
          name: 'ObjectRecordDetail',
          component: () => import('../views/custom-objects/ObjectRecordDetail.vue'),
        },
        {
          path: 'admin/territories',
          name: 'TerritoryList',
          component: () => import('../views/territories/TerritoryList.vue'),
        },
        {
          path: 'admin/territories/new',
          name: 'TerritoryCreate',
          component: () => import('../views/territories/TerritoryForm.vue'),
        },
        {
          path: 'admin/territories/:id',
          name: 'TerritoryDetail',
          component: () => import('../views/territories/TerritoryDetail.vue'),
        },
        {
          path: 'admin/territories/:id/edit',
          name: 'TerritoryEdit',
          component: () => import('../views/territories/TerritoryForm.vue'),
        },
        {
          path: 'admin/workflows',
          name: 'WorkflowList',
          component: () => import('../views/workflows/WorkflowList.vue'),
        },
        {
          path: 'admin/workflows/new',
          name: 'WorkflowCreate',
          component: () => import('../views/workflows/WorkflowBuilder.vue'),
        },
        {
          path: 'admin/workflows/:id',
          name: 'WorkflowDetail',
          component: () => import('../views/workflows/WorkflowBuilder.vue'),
        },
        {
          path: 'admin/reports',
          name: 'ReportList',
          component: () => import('../views/reports/ReportList.vue'),
        },
        {
          path: 'admin/reports/new',
          name: 'ReportCreate',
          component: () => import('../views/reports/ReportBuilder.vue'),
        },
        {
          path: 'admin/reports/:id/edit',
          name: 'ReportEdit',
          component: () => import('../views/reports/ReportBuilder.vue'),
        },
        {
          path: 'admin/dashboards',
          name: 'DashboardPage',
          component: () => import('../views/reports/DashboardPage.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated && localStorage.getItem('access_token')) {
    try {
      await auth.fetchUser()
    } catch {
      auth.logout()
    }
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && auth.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
