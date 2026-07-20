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
          path: 'events',
          name: 'EventList',
          component: () => import('../views/events/EventList.vue'),
        },
        {
          path: 'events/new',
          name: 'EventCreate',
          component: () => import('../views/events/EventForm.vue'),
        },
        {
          path: 'events/:id',
          name: 'EventDetail',
          component: () => import('../views/events/EventDetail.vue'),
        },
        {
          path: 'events/:id/edit',
          name: 'EventEdit',
          component: () => import('../views/events/EventForm.vue'),
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
          path: 'admin/territories/:id',
          redirect: '/admin/territories',
        },
        {
          path: 'admin/territories/:id/edit',
          redirect: '/admin/territories',
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
        {
          path: 'admin/settings',
          name: 'Settings',
          component: () => import('../views/admin/SettingsPage.vue'),
        },
        {
          path: 'admin/notifications',
          name: 'NotificationList',
          component: () => import('../views/admin/NotificationList.vue'),
        },
        {
          path: 'admin/approval-queue',
          name: 'ApprovalQueue',
          component: () => import('../views/admin/ApprovalQueue.vue'),
        },
        {
          path: 'admin/recycle-bin',
          name: 'RecycleBin',
          component: () => import('../views/admin/RecycleBin.vue'),
        },
        {
          path: 'campaigns',
          name: 'CampaignList',
          component: () => import('../views/campaigns/CampaignList.vue'),
        },
        {
          path: 'campaigns/new',
          name: 'CampaignCreate',
          component: () => import('../views/campaigns/CampaignForm.vue'),
        },
        {
          path: 'campaigns/:id',
          name: 'CampaignDetail',
          component: () => import('../views/campaigns/CampaignDetail.vue'),
        },
        {
          path: 'campaigns/:id/edit',
          name: 'CampaignEdit',
          component: () => import('../views/campaigns/CampaignForm.vue'),
        },
        {
          path: 'leads',
          name: 'LeadList',
          component: () => import('../views/leads/LeadList.vue'),
        },
        {
          path: 'leads/new',
          name: 'LeadCreate',
          component: () => import('../views/leads/LeadForm.vue'),
        },
        {
          path: 'leads/:id',
          name: 'LeadDetail',
          component: () => import('../views/leads/LeadDetail.vue'),
        },
        {
          path: 'leads/:id/edit',
          name: 'LeadEdit',
          component: () => import('../views/leads/LeadForm.vue'),
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('../views/profile/ProfilePage.vue'),
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
