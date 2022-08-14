<template>
  <div class="classCard">
    <div class="classInfo" :class="h.categorie">
      <div class="hmeta">
        <span>🕓 {{ this.$tsHm(h.h_debut) }} à {{ h.h_fin }}</span>
        <span v-if="h.amphi">🏦 {{ h.amphi }}</span>
        <span v-else>🏦 400</span>
        <span class="hens" v-if="h.ens">👩🏿‍🏫 {{ h.ens }}</span>
      </div>
      <div class="hintitule">
        <span class="intitule">{{ h.intitule }}</span>
      </div>
      <div><button @click="showModalEditClass()" rel="noopener noreferrer" v-if="hasPlanningRights">
      Modifier le cours 
    </button></div>
    </div>
    <ClassRoneo v-bind:h="h" v-bind="$attrs" />
  </div>
</template>

<script>
import ClassRoneo from "./ClassRoneo.vue";
export default {
  components: { ClassRoneo },
  props: {
    h: Object,
  },
  data() {
    return {
      hasPlanningRights: false,
    }
  },
  mounted() {
    this.hasPlanningRights = this.$store.getters["auth/hasPlanningRights"];
  },
  methods: {
    showModalEditClass() {
      if (!this.$store.getters["auth/isAuthenticated"]) {
        this.$router.push("login");
      } else {
        this.$emit("showModalEditClass", {
          h: this.h,
        });
      }
    },
  }
};
</script>

<style>
.classCard {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: space-between;
  margin-bottom: 0.4em;
}
.classInfo {
  padding: 0.3em;
  width: 55%;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
}
.hmeta {
  display: flex;
  justify-content: center;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: space-evenly;
}
.hmeta > span {
  margin-inline: 1em;
}
.hintitule {
  border-style: groove;
  /* margin-inline: 1em; */
  padding-inline: 0.2em;
  padding-block: 0.2em;
  text-align: justify-all;
  text-justify: inter-word;
  text-align-last: center;
  word-break: keep-all;
}

div[class^='TP:AnatomieUE3.1'], div[class*=' TP:AnatomieUE3.1'] {
  background-color: rgb(5, 153, 153);
}
div[class^='ED:Pharmaco'], div[class*=' ED:Pharmaco'] {
  background-color: rgb(117, 247, 247);
}
div[class^='TP:Histologie'], div[class*=' TP:Histologie'] {
  background-color: lightcyan;
}
.UrgVit {
  background-color: #528dd4;
}
.ECOS {
  background-color: #00af50;
}
.MB {
  background-color: white;
}
.CC {
  background-color: #92d050;
}
.BioSens {
  background-color: #ff9b0e;
}
.SSES {
  background-color: #a9d08e;
}
.SESA {
  background-color: #cafcc5;
}
.Ophtalmologie {
  background-color: #ffff00;
}
.AFGSU {
  background-color: #3b46ff;
}
.LCA {
  background-color: white;
}
.Pres {
  background-color: #756aff;
}
.ECN {
  background-color: #64db1f;
}
.StageSemio {
  background-color: #ff0000;
}
.UE1 {
  background-color: white;
}
.UE2 {
  background-color: white;
}
.UE3 {
  background-color: white;
}
.UE4 {
  background-color: white;
}
.UE5 {
  background-color: white;
}
.UE6 {
  background-color: white;
}
.UE7 {
    background-color: darkseagreen;
}
.UE8 {
    background-color: darkseagreen;
}
.UE9 {
    background-color: darkseagreen;
}
.UE10 {
    background-color: darkorange;
}
.UE11 {
    background-color: aliceblue;
}
.UE12 {
    background-color: burlywood;
}
.UE13 {
    background-color: darksalmon;
}
.UE14 {
    background-color: greenyellow;
}
.CUESIM {
  background-color: #00afef;
}
.MI {
  background-color: white;
}
.CasClin {
  background-color: white;
}
.EDpharma {
  background-color: #00afef;
}
.EDanat {
  background-color: #cafcc5;
}
.EDhisto {
  background-color: #adaaaa;
}
.examen {
  background-color: #ffff00;
}
</style>