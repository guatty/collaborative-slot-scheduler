<template>
  <h2>Inscription FGSM3 (D1)</h2>
  <img
    id="profile-img"
    src="../assets/avatar_anonymous.png"
    class="profile-img-card"
  />
  <Form @submit="handleRegister" :validation-schema="schema">
    <div v-if="!successful" class="registerform">
      <div class="inputfield">
        <label for="firstname">Prénom</label>
        <Field name="firstname" type="text" class="form-control" />
        <ErrorMessage name="firstname" class="error-feedback" />
      </div>
      <div class="inputfield">
        <label for="lastname">Nom</label>
        <Field name="lastname" type="text" class="form-control" />
        <ErrorMessage name="lastname" class="error-feedback" />
      </div>
      <div class="inputfield">
        <label for="mail">Adresse mail</label>
        <Field name="mail" type="email" class="form-control" />
        <ErrorMessage name="mail" class="error-feedback" />
      </div>
      <div class="inputfield">
        <label for="password">Mot de passe</label>
        <Field name="password" type="text" class="form-control" />
        <ErrorMessage name="password" class="error-feedback" />
      </div>
      <p class="terms">Pour le bon fonctionnement de l’association, je m’engage à faire le meilleur cours possible. <br/><br/>

Ainsi, je respecte au maximum la date limite de la rédaction et de la relecture des cours. Je prends l’initiative de prévenir le relecteur ou les admins dans le cas où je serais en retard. <br/>
Je suis un·e étudiant·e responsable et je favorise toujours la communication avec mes camarades.<br/><br/>

Je suis conscient·e que des êtres humains ont participé à l’écriture des ronéos, donc je n’abuse pas de la patience de mes camarades, je respecte mes camarades ainsi que leurs travaux.</p>
      <label for="terms"
        >En vous inscrivant, vous vous engagez à respecter les conditions de
        l'APECS</label
      >
      <!-- <label for="terms">Je m'engage</label> -->
      <!-- <input name="terms" type="checkbox" class="form-control" />
        <ErrorMessage name="terms" class="error-feedback" /> -->
      <br />
      <button class="btn btn-primary btn-block" :disabled="loading">
        <span v-show="loading" class="spinner-border spinner-border-sm"></span>
        Inscription
      </button>
      <br /><br />
      <em>Un mail sera envoyé pour confirmer l'adresse mail renseignée</em
      ><br />
    </div>
  </Form>

  <div
    v-if="message"
    class="alert"
    :class="successful ? 'alert-success' : 'alert-danger'"
  >
    {{ message }}
  </div>
</template>

<script>
import { Form, Field, ErrorMessage } from "vee-validate";
import * as yup from "yup";

export default {
  name: "Register",
  components: {
    Form,
    Field,
    ErrorMessage,
  },
  data() {
    const schema = yup.object().shape({
      firstname: yup
        .string()
        .required("Ce champ est obligatoire")
        .min(1, "Doit faire au moins 1 caractère !")
        .max(50, "Ne doit pas faire plus de 50 caractères !"),
      lastname: yup
        .string()
        .required("Ce champ est obligatoire")
        .min(1, "Doit faire au moins 1 caractère !")
        .max(50, "Ne doit pas faire plus de 50 caractères !"),
      mail: yup
        .string()
        .required("Ce champ est obligatoire")
        .email("Adresse mail invalide !")
        .max(50, "Ne doit pas faire plus de 50 caractères !"),
      password: yup
        .string()
        .required("Ce champ est obligatoire")
        .min(6, "Doit faire au moins 6 caractères !")
        .max(40, "Ne doit pas faire plus de 40 caractères !"),
      // terms: yup
      //   .boolean()
      //   .required("Ce champ est obligatoire")
      //   .oneOf([true], 'Ce champ est obligatoire'),
    });

    return {
      successful: false,
      loading: false,
      message: "",
      schema,
    };
  },
  computed: {
    loggedIn() {
      return this.$store.state.auth.status.loggedIn;
    },
  },
  mounted() {
    if (this.loggedIn) {
      this.$router.push("/");
    }
  },
  methods: {
    handleRegister(user) {
      this.message = "";
      this.successful = false;
      this.loading = true;

      this.$store.dispatch("auth/registerD1", user).then(
        (data) => {
          this.message = data.message;
          this.successful = true;
          this.loading = false;
          this.$router.push("/D1/login");
        },
        (error) => {
          this.message =
            (error.response &&
              error.response.data &&
              error.response.data.message) ||
            error.message ||
            error.toString();
          this.successful = false;
          this.loading = false;
        }
      );
    },
  },
};
</script>

<style>
.registerform {
  display: grid;
  grid-template-columns: 1fr;
  justify-items: center;
}

.error-feedback {
  background-color: #f44336; /* Red */
  color: white;
  padding: 8px;
  grid-column: span 2;
  margin-top: 3px;
  margin-bottom: 10px
}

.inputfield {
  display: grid;
  grid-template-columns: 1fr 2fr;
  grid-template-rows: 1fr 1fr;
  justify-items: center;
}

input,
select,
textarea {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

label {
  padding: 12px 12px 12px 0;
  display: inline-block;
}

.terms {
  background-color: #e6e6e6;
  padding-inline: 40px;
}

input[type="submit"] {
  background-color: #04aa6d;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  float: right;
}

input[type="submit"]:hover {
  background-color: #45a049;
}

/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}

/* Responsive layout - when the screen is less than 600px wide, make the two columns stack on top of each other instead of next to each other */
@media screen and (max-width: 600px) {
  input[type="submit"] {
    width: 100%;
    margin-top: 0;
  }
  .inputfield {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr 1fr 1fr;
  justify-items: center;
}
}
</style>
