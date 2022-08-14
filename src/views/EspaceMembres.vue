<template>
  <div class="home">
    <h3>
      Merci pour ton engagement, {{userFirstname}} {{userLastname}} ! ^^ <br>
      Si tu souhaites participer à l'amélioration de la plateforme ainsi qu'à la vie de l'APECS, les recrutements sont toujours ouverts ! 
    </h3>
    <button :onclick="logout" style="background-color: #ff1403; color: white">
      Déconnexion
    </button>
    <UserParams />
    <h2>Rappel des créneaux que vous avez choisis :</h2>
    <h3>
      <em
        >Remarque : Pour information les créneaux et les noms des autres membres
        de l'APECS du même horaire sont indiqués</em
      >
    </h3>
    <Planning v-if="!hasNoData" :horaires="horaires" />
    <h2 v-else>Vous n'avez pas pris de créneau pour le moment.</h2>
  </div>
</template>

<script>
import Planning from "../components/Planning.vue";
import UserParams from "../components/UserParams.vue";
import { Http } from "@capacitor-community/http";
export default {
  name: "EspaceMembres",
  components: { Planning, UserParams },
  data() {
    return { horaires: [], hasNoData: false };
  },
  computed: {
    loggedIn() {
      return this.$store.getters["auth/isAuthenticated"];
    },
    userFirstname() {
      return this.$store.getters["auth/userFirstname"];
    },
    userLastname() {
      return this.$store.getters["auth/userLastname"];
    },
  },
  created() {
    if (!this.loggedIn) {
      this.$router.push({ name: "LoginP2" });
    }
  },
  mounted() {
    this.refreshUserPlanning();
  },
  methods: {
    logout() {
      this.$store.dispatch("auth/logout");
      this.$router.push({ name: "LoginP2" });
    },
    async refreshUserPlanning() {
      this.horaires = [];

      await Http.request({
        method: "GET",
        url: this.$API_URL + "/myPlanning",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
      })
        .then(({ data }) => {
          if (data.length) {
            this.horaires = data;
          } else {
            this.hasNoData = true;
          }
        })
        .catch((err) => console.log(err));
    },
  },
};
</script>