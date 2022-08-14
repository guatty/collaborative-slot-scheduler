<template>
  <div id="nav">
    <router-link v-if="isAuthenticatedEvenIfExpired" :to="{ name: 'MiniPlanningD1' }" >Mini-planning</router-link>
    <router-link v-if="!isAuthenticatedEvenIfExpired" :to="{ name: 'LoginD1' }" id="normal-nav">Mini-planning</router-link>
    <router-link :to="{ name: 'GlobalPlanningD1' }">Planning Global</router-link>
    <router-link v-if="isAuthenticatedEvenIfExpired" :to="{ name: 'EspaceMembresD1' }">Espace Membres</router-link>
    <router-link v-if="!isAuthenticatedEvenIfExpired" :to="{ name: 'LoginD1' }">Connexion</router-link>
    <router-link v-if="hasMembersManagementRights" :to="{ name: 'MembresD1' }" class="buttonadmin">Membres D1</router-link>
    <!-- <button v-if="deferredPrompt" @click="install" rel="noopener noreferrer">Installer l'application</button> -->
    <a href="https://drive.google.com/drive/u/0/folders/1KcmqNcB7GXQWBxt3-9xIXkqvyL4PI98X" class="buttondrive" target="_blank">📁 Drive D1</a>
  </div>
  <GlobalPlanningD1 v-if="$route.name === 'FGSM3'" />
  <router-view v-else />
</template>


<script>
import GlobalPlanningD1 from "@/components/GlobalPlanningD1.vue";
export default {
  components: {
    GlobalPlanningD1
  },
  computed: {
    isAuthenticatedEvenIfExpired () {
      return this.$store.getters['auth/isAuthenticatedEvenIfExpired'];
    },
    hasMembersManagementRights() { 
      return this.$store.getters["auth/hasMembersManagementRights"];
    },
  },
  data() {
    return {
      deferredPrompt: null
    };
  },
  created() {
    window.addEventListener("beforeinstallprompt", e => {
      e.preventDefault();
      // Stash the event so it can be triggered later.
      this.deferredPrompt = e;
    });
    window.addEventListener("appinstalled", () => {
      this.deferredPrompt = null;
    });
  },
  methods: {
    async dismiss() {
      this.deferredPrompt = null;
    },
    async install() {
      this.deferredPrompt.prompt();
    }
  }
};
</script>


<style>
@font-face {
  font-family: 'Noto Color Emoji';
  src: url(https://gitcdn.xyz/repo/googlefonts/noto-emoji/master/fonts/NotoColorEmoji.ttf);
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif, 'Segoe UI Symbol', 'Apple Symbols', 'Noto Sans Symbols', 'Twemoji Mozilla', 'Apple Color Emoji', 'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin: 0 auto;
}

#nav {
  display: flex;
  justify-content: center;
  flex-flow: row wrap;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  padding: 10px;
  border-radius: 4px;
}

#nav a.router-link-exact-active {
  color: white;
  background: #1c5aa0;
}
#nav #normal-nav {
  color: #2c3e50;
  background: white;
}

button, .buttondrive, .buttonadmin {
  margin: 0 10px;
  padding: 10px;
  border: none;
  border-radius: 4px;
}

.buttondrive {
  font-weight: bolder;
  background-color: #ffff00;
}
.buttonadmin {
  font-weight: bolder;
  background-color: orangered;
}


#header {
  display: flex;
  align-items: center;
  justify-content: center;
}
#header h1 {
  font-family: "Roboto", sans-serif;
  display: block;
}
#header img {
  vertical-align: middle;
  height: 9em;
}
.apecs {
  color: #1c5aa0;
  font-weight: bold;
}
.ml {
  color: #1c5aa0;
  font-weight: bold;
}
</style>
