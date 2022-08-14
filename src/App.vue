<template>
    <div id="header">
      <img alt="Vue logo" src="./assets/APECS-ABEILLE-CADUCEE.png" />
      <h1>
        <span class="apecs">APECS</span>
        <br /><span class="ml">M</span>édecine <br /><span class="ml">L</span>orraine
      </h1>
    </div>
  <div id="nav">
    <router-link :to="{ name: 'FGSM2' }" :class="{isactivated: isInP2}" >FGSM2 (P2)</router-link>
    <button v-if="deferredPrompt" @click="install" rel="noopener noreferrer">Installer<br/>l'application</button>
    <router-link :to="{ name: 'FGSM3' }" :class="{isactivated: isInD1}" >FGSM3 (D1)</router-link>
  </div>
  <router-view v-if="isInP2|isInD1"/>
  <div v-else id="bruh">
    <router-link :to="{ name: 'FGSM2' }" >
    <div class="squarem2">
      <h2>FGSM2 (P2)</h2>
      <p>Accéder à la plateforme pour les 2ème année.</p>
    </div>
    </router-link>
    <router-link :to="{ name: 'FGSM3' }" >
    <div class="squarem3">
      <h2>FGSM3 (D1)</h2>
      <p>Accéder à la plateforme pour les 3ème année.</p>
    </div>
    </router-link>
  </div>
</template>

<script>
export default {
  computed: {
    isAuthenticatedEvenIfExpired () {
      return this.$store.getters['auth/isAuthenticatedEvenIfExpired'];
    },
    hasMembersManagementRights() { 
      return this.$store.getters["auth/hasMembersManagementRights"];
    },
    isInP2() {
      return this.$route.name != null && (this.$route.name.includes('P2') || this.$route.name.includes('FGSM2'));
    },
    isInD1() {
      return this.$route.name != null && (this.$route.name.includes('D1') || this.$route.name.includes('FGSM3'));
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

#bruh {
  display: flex;
  justify-content: space-around;
}

.squarem2 {
  color:#ffff00;
  background-color:#1c5aa0;
  border-style: solid;
  border-width: 10px;
  width: 200px;
  height: 200px;
  text-align: center;
}

.squarem3 {
  background-color:#ffff00;
  color:#1c5aa0;
  border-style: solid;
  border-width: 10px;
  width: 200px;
  height: 200px;
  text-align: center;
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

#nav a.isactivated {
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
