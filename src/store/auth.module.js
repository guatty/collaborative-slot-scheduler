import AuthService from '../services/auth.service';
import Cookies from 'js-cookie'

Cookies.remove('user');
const user = JSON.parse(localStorage.getItem('user'));
const initialState = user ?
  {
    status: {
      loggedIn: true
    },
    user
  } :
  {
    status: {
      loggedIn: false
    },
    user: null
  };

const isValidJwt = (jwt) => {
  if (!isValidOrExpiredJwt(jwt)) {
    return false
  }
  const data = JSON.parse(atob(jwt.split('.')[1]))
  const exp = new Date(data.exp * 1000)
  const now = new Date()
  return now < exp
}

const isValidOrExpiredJwt = (jwt) => {
  return jwt && jwt.split('.').length == 3;
}

export const auth = {
  namespaced: true,
  state: initialState,
  actions: {
    login({
      commit
    }, user) {
      return AuthService.login(user).then(
        user => {
          commit('loginSuccess', user);
          return Promise.resolve(user);
        },
        error => {
          commit('loginFailure');
          return Promise.reject(error);
        }
      );
    },
    logout({
      commit
    }) {
      AuthService.logout();
      commit('logout');
    },
    registerP2({
      commit
    }, user) {
      return AuthService.registerP2(user).then(
        response => {
          commit('registerSuccess');
          return Promise.resolve(response.data);
        },
        error => {
          commit('registerFailure');
          return Promise.reject(error);
        }
      );
    },
    registerD1({
      commit
    }, user) {
      return AuthService.registerD1(user).then(
        response => {
          commit('registerSuccess');
          return Promise.resolve(response.data);
        },
        error => {
          commit('registerFailure');
          return Promise.reject(error);
        }
      );
    }
  },
  mutations: {
    loginSuccess(state, user) {
      state.status.loggedIn = true;
      state.user = user;
    },
    loginFailure(state) {
      state.status.loggedIn = false;
      state.user = null;
    },
    logout(state) {
      state.status.loggedIn = false;
      state.user = null;
    },
    registerSuccess(state) {
      state.status.loggedIn = false;
    },
    registerFailure(state) {
      state.status.loggedIn = false;
    }
  },
  getters: {
    isAuthenticated(state) {
      return state.user !== null && isValidJwt(state.user.token);
    },
    isAuthenticatedEvenIfExpired(state) {
      return state.user !== null && isValidOrExpiredJwt(state.user.token);
    },
    userFirstname(state) {
      if(state.user !== null) {
        return state.user.firstname;
      } else{
        return "N/A";
      }
    },
    userLastname(state) {
      if(state.user !== null) {
        return state.user.lastname;
      } else{
        return "N/A";
      }
    },
    getJWT(state) {
      if (state.user == null) {
        return null;
      } else {
        return state.user.token;
      }
    },
    hasPlanningRights(state) {
      if (state.user == null) {
        return false;
      } else {
        return state.user.hasPlanningRights;
      }
    },
    hasEditionRights(state) {
      if (state.user == null) {
        return false;
      } else {
        return state.user.hasEditionRights;
      }
    },
    hasMembersManagementRights(state) {
      if (state.user == null) {
        return false;
      } else {
        return state.user.hasMembersManagementRights;
      }
    },
    identity(state) {
      if (state.user == null) {
        return null;
      } else {
        return {
          firstname: state.user.firstname,
          lastname: state.user.lastname,
        }
      }
    },
  }
};