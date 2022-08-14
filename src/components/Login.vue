<template>
  <div class="login">
    <img
      id="profile-img"
      src="../assets/avatar_anonymous.png"
      class="profile-img-card"
    />
    <Form class="login-form" @submit="handleLogin" :validation-schema="schema">
      <div class="form-group">
        <label for="mail">Adresse mail</label>
        <Field name="mail" type="text" class="form-control" />
        <ErrorMessage name="mail" class="error-feedback" />
      </div>
      <div class="form-group">
        <label for="password">Mot de passe</label>
        <Field name="password" :type="dispPasswordType" class="form-control" />
        <ErrorMessage name="password" class="error-feedback" />
      </div>
      <div class="form-group">
        <label for="dispPassword">Afficher le mot de passe?</label>
        <input name="dispPassword" type="checkbox" class="form-control" v-model="dispPassword" />
      </div>

      <div class="form-group">
        <button class="buttonwithloader" :disabled="loading">
          <span v-show="loading" class="loaderr"></span>
          <span>Connexion</span>
        </button>
      </div>

      <div class="form-group">
        <div v-if="message" class="alert alert-danger" role="alert">
          {{ message }}
        </div>
      </div>
    </Form>
  </div>
</template>

<script>
import { Form, Field, ErrorMessage } from "vee-validate";
import * as yup from "yup";

export default {
  name: "LoginP2",
  components: {
    Form,
    Field,
    ErrorMessage,
  },
  data() {
    const schema = yup.object().shape({
      mail: yup.string().required("Veuillez entrer votre adresse mail"),
      password: yup.string().required("Veuillez entrer votre mot de passe"),
    });

    return {
      loading: false,
      message: "",
      schema,
      dispPassword: false,
    };
  },
  computed: {
    loggedIn() {
      return this.$store.getters["auth/isAuthenticated"];
    },
    dispPasswordType() {
      if(this.dispPassword){
        return "text"
      } else {
        return "password"
      }
    },
  },
  created() {
    if (this.loggedIn) {
      this.$router.push('/');
    }
  },
  methods: {
    toggleDispPassword() {
      this.dispPassword = !this.dispPassword;
    },
    handleLogin(user) {
      this.loading = true;

      this.$store.dispatch("auth/login", user).then(
        () => {
          this.$router.push('/');
        },
        (error) => {
          console.log(error)
          this.loading = false;
          this.message =
            (error.response &&
              error.response.data &&
              error.response.data.message) ||
            error.message ||
            error.toString();
        }
      );
    },
  },
};
</script>

<style scoped>
.loaderr {
  border: 10px solid #f3f3f3; /* Light grey */
  border-top: 10px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 15px;
  height: 15px;
  animation: spin 2s linear infinite;
  display: inline-block;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

* {
  box-sizing: border-box;
}

input, select, textarea {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

label {
  padding: 12px 12px 12px 0;
  display: inline-block;
}

input[type=submit] {
  background-color: #04AA6D;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  float: right;
}

input[type=submit]:hover {
  background-color: #45a049;
}

.container {
  border-radius: 5px;
  background-color: #f2f2f2;
  padding: 20px;
}

.col-25 {
  float: left;
  width: 25%;
  margin-top: 6px;
}

.col-75 {
  float: left;
  width: 75%;
  margin-top: 6px;
}

/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}

/* Responsive layout - when the screen is less than 600px wide, make the two columns stack on top of each other instead of next to each other */
@media screen and (max-width: 600px) {
  .col-25, .col-75, input[type=submit] {
    width: 100%;
    margin-top: 0;
  }
}
</style>