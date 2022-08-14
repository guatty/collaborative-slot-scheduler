<template>
  <h3>Pas de compte ? <router-link :to="{ name: 'RegisterP2' }">Inscription FGSM2 (P2)</router-link></h3>
  <Login/>
</template>

<script>
import Login from "../components/Login.vue"
export default {
  name: "LoginP2",
  components: {
    Login
  },
};
</script>

<style>
</style>