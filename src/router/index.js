import {
  createRouter,
  createWebHistory
} from 'vue-router'
import SubsiteP2 from '../views/SubsiteP2.vue'
import SubsiteD1 from '../views/SubsiteD1.vue'
import MiniPlanningP2 from '../components/MiniPlanningP2.vue'
import MiniPlanningD1 from '../components/MiniPlanningD1.vue'
import EspaceMembres from '../views/EspaceMembres.vue'
import MembresP2 from '../views/MembresP2.vue'
import MembresD1 from '../views/MembresD1.vue'
import LoginP2 from '../components/LoginP2.vue'
import LoginD1 from '../components/LoginD1.vue'
import GlobalPlanningP2 from '../components/GlobalPlanningP2.vue'
import GlobalPlanningD1 from '../components/GlobalPlanningD1.vue'
import RegisterP2 from '../components/RegisterP2.vue'
import RegisterD1 from '../components/RegisterD1.vue'
import store from '../store'

const routes = [
  {
    path: '/P2/',
    component: SubsiteP2,
    name: 'FGSM2',
    children: [{
        path: '/P2/MiniPlanning',
        name: 'MiniPlanningP2',
        component: MiniPlanningP2
      },
      {
        path: '/P2/planningGlobal',
        name: 'GlobalPlanningP2',
        component: GlobalPlanningP2
      },
      {
        path: '',
        name: 'HomeP2',
        component: GlobalPlanningP2
      },
      {
        path: '/P2/EspaceMembres',
        name: 'EspaceMembresP2',
        component: EspaceMembres
      },
      {
        path: '/P2/login',
        name: 'LoginP2',
        component: LoginP2
      },
      {
        path: '/P2/register',
        name: 'RegisterP2',
        component: RegisterP2
      },
      {
        path: '/P2/membres',
        name: 'MembresP2',
        component: MembresP2
      },
    ],
  },
  {
    path: '/D1/',
    component: SubsiteD1,
    name: 'FGSM3',
    children: [{
        path: '/D1/MiniPlanning',
        name: 'MiniPlanningD1',
        component: MiniPlanningD1
      },
      {
        path: '/D1/PlanningGlobal',
        name: 'GlobalPlanningD1',
        component: GlobalPlanningD1
      },
      {
        path: '',
        name: 'HomeD1',
        component: GlobalPlanningD1
      },
      {
        path: '/D1/EspaceMembres',
        name: 'EspaceMembresD1',
        component: EspaceMembres
      },
      {
        path: '/D1/login',
        name: 'LoginD1',
        component: LoginD1
      },
      {
        path: '/D1/register',
        name: 'RegisterD1',
        component: RegisterD1
      },
      {
        path: '/D1/membresD1',
        name: 'MembresD1',
        component: MembresD1
      },
    ],
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register', '/', '/planningGlobal', 'P2', 'D1', '/P2/login', '/P2/register', '/P2/', '/P2/planningGlobal', '/D1/login', '/D1/register', '/D1/', '/D1/PlanningGlobal'];
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = store.getters['auth/isAuthenticatedEvenIfExpired'];

  // trying to access a restricted page + not logged in
  // redirect to login page
  if (authRequired && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router