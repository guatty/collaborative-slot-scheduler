<template>
  <div id="nav">
    <router-link v-if="isAuthenticatedEvenIfExpired" :to="{ name: 'MiniPlanningP2'}" >Mini-planning</router-link>
    <router-link v-if="!isAuthenticatedEvenIfExpired" :to="{ name: 'LoginP2' }" id="normal-nav">Mini-planning</router-link>
    <router-link :to="{ name: 'GlobalPlanningP2' }">Planning Global</router-link>
    <router-link v-if="isAuthenticatedEvenIfExpired" :to="{ name: 'EspaceMembresP2' }">Espace Membres</router-link>
    <router-link v-if="!isAuthenticatedEvenIfExpired" :to="{ name: 'LoginP2' }">Connexion</router-link>
    <router-link v-if="hasMembersManagementRights" :to="{ name: 'MembresP2' }" class="buttonadmin">Membres P2</router-link>
    <!-- <button v-if="deferredPrompt" @click="install" rel="noopener noreferrer">Installer l'application</button> -->
    <a href="https://drive.google.com/drive/folders/12-t_z-6Oe6PUvyY9zJ8u-1mtG2M7St4U" class="buttondrive" target="_blank">📁 Drive P2</a>
  </div>
  <GlobalPlanningP2 v-if="$route.name === 'FGSM2'" />
  <router-view v-else />
</template>


<script>
import GlobalPlanningP2 from "@/components/GlobalPlanningP2.vue";
export default {
  components: {
    GlobalPlanningP2
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
