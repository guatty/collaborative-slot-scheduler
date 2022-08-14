<template>
  <h3>Pas de compte ? <router-link :to="{ name: 'RegisterD1' }">Inscription FGSM3 (D1)</router-link></h3>
  <Login/>
</template>

<script>
import Login from "../components/Login.vue"
export default {
  name: "LoginD1",
  components: {
    Login
  },
};
</script>

<style>
</style>