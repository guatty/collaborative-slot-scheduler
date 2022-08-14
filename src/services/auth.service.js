import {
  Http
} from "@capacitor-community/http";
import Cookies from 'js-cookie'

const API_URL = process.env.VUE_APP_APIURL === undefined ? "https://www.apecs.ml" : process.env.VUE_APP_APIURL;
class AuthService {
  login(user) {
    return new Promise((resolve, reject) => {
      Http.request({
        method: "POST",
        url: API_URL + "/signin",
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          mail: user.mail,
          password: user.password
        },
      }).then(({
        data
      }) => {
        console.log(data)
        if (data.token) {
          localStorage.setItem('user', JSON.stringify(data));
          Cookies.set('user', JSON.stringify(data));
          resolve(data);
        } else {
          reject(new Error(data.message));
        }
      })
    });
  }

  logout() {
    localStorage.removeItem('user');
    Cookies.remove('user');
  }

  registerP2(user) {
    return Http.request({
      method: "POST",
      url: API_URL + "/signup",
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
      data: {
        firstname: user.firstname,
        lastname: user.lastname,
        mail: user.mail,
        password: user.password,
        facebook: '',
        discord: '',
        school_year: 'P2_2026',
      }
    });
  }

  registerD1(user) {
    return Http.request({
      method: "POST",
      url: API_URL + "/signup",
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      },
      data: {
        firstname: user.firstname,
        lastname: user.lastname,
        mail: user.mail,
        password: user.password,
        facebook: '',
        discord: '',
        school_year: 'D1_2025',
      }
    });
  }
}

export default new AuthService();