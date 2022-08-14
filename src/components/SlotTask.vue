
<script>
import { Http } from "@capacitor-community/http";
export default {
  props: {
    kind_str_fr: String,
    kind_str_en: String,
    kind_obj: Object,
    ts: Object,
    h: Object,
  },
  data() {
    return {
      isThyself: false,
      hasStarted: false,
      hasFinished: false,
      hasPlanningRights: false,
      loading: false,
      loadingCancel: false,
      hasPreloaded: false,
      coursCommence: true,
    };
  },
  computed: {
    canDelete() {
      return this.hasPlanningRights || (false && this.isThyself && !this.hasStarted);
    },
    slot_kind_prise() {
      return this.kind_str_fr + "_prise";
    },
  },
  mounted() {
    this.coursCommence = this.h.h_debut *1000 < Date.now();
    this.hasPlanningRights = this.$store.getters["auth/hasPlanningRights"];
    var identity = this.$store.getters["auth/identity"]
    if (this.kind_obj != null) {
      this.hasStarted = this.ts[this.kind_str_fr+"_started"];
      this.hasFinished = this.ts[this.kind_str_fr+"_finished"];
      if(identity != null) {
        this.isThyself = identity.firstname == this.kind_obj.firstname && identity.lastname == this.kind_obj.lastname;
      }
    }
    this.hasPreloaded = true;
  },
  methods: {
    async fetchIsThyself() {
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/isThyself",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          user: this.kind_obj,
        },
      }).then((data) => {
        this.isThyself = data.data.resp;
      });
    },
    async setStarted() {
      this.loading = true;
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/setStarted",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          timestamp_start: this.ts.s_begin,
          timestamp_end: this.ts.s_end,
          class_id: this.h.class_id,
          timeslot_kind: this.kind_str_fr,
        },
      }).then(() => {
        this.loading = false;
        this.hasStarted = true;
      });
    },
    async setFinished() {
      this.loading = true;
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/setFinished",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          timestamp_start: this.ts.s_begin,
          timestamp_end: this.ts.s_end,
          class_id: this.h.class_id,
          timeslot_kind: this.kind_str_fr,
        },
      }).then(() => {
        this.loading = false;
        this.hasFinished = true;
      });
    },
    async cancelStarted() {
      this.loadingCancel = true;
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/cancelStarted",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          timestamp_start: this.ts.s_begin,
          timestamp_end: this.ts.s_end,
          class_id: this.h.class_id,
          timeslot_kind: this.kind_str_fr,
        },
      }).then(() => {
        this.loadingCancel = false;
        this.hasStarted = false;
      });
    },
    async cancelFinished() {
      this.loadingCancel = true;
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/cancelFinished",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          timestamp_start: this.ts.s_begin,
          timestamp_end: this.ts.s_end,
          class_id: this.h.class_id,
          timeslot_kind: this.kind_str_fr,
        },
      }).then(() => {
        this.loadingCancel = false;
        this.hasFinished = false;
      });
    },
    showModalThyself() {
      if (!this.$store.getters["auth/isAuthenticated"]) {
        this.$router.push("login");
      } else {
        this.$emit("showModal", {
          h: this.h,
          ts: this.ts,
          kind: this.kind_str_fr,
        });
      }
    },
    showModalAssignOther() {
      if (!this.$store.getters["auth/isAuthenticated"]) {
        this.$router.push("login");
      } else {
        this.$emit("showModalAssignOther", {
          h: this.h,
          ts: this.ts,
          kind: this.kind_str_fr
        });
      }
    },
    confirmDelete() {
      if (!this.$store.getters["auth/isAuthenticated"]) {
        this.$router.push("login");
      } else {
        this.$emit("showModalConfirmDelete", {
          h: this.h,
          ts: this.ts,
          kind: this.kind_str_fr,
        });
      }
    },
  },
};
</script>

<template>
  <span v-show="!hasPreloaded" class="loaderr"></span>
  <span v-if="kind_obj" v-show="hasPreloaded"
    >{{ kind_obj.firstname }} {{ kind_obj.lastname }}
    <template v-if="isThyself">
      <br />
      <button
        v-if="!hasStarted && kind_str_fr!='edition'"
        @click="setStarted()"
        rel="noopener noreferrer"
      >
        J'ai Commencé !
        <span v-show="loading" class="loaderr"></span>
      </button>
      <span v-else-if="!hasFinished">
        <button @click="setFinished()" rel="noopener noreferrer">
          J'ai Fini !
          <span v-show="loading" class="loaderr"></span>
        </button>
        <button @click="cancelStarted()" rel="noopener noreferrer">⏮️<span v-show="loadingCancel" class="loaderr"></span></button>
      </span>
      <span v-else
        >Merci à toi !! 😊
        <button @click="cancelFinished()" rel="noopener noreferrer">
          ⏮️<span v-show="loadingCancel" class="loaderr"></span>
        </button>
      </span>
    </template>
    <template v-else-if="!coursCommence">
      <br />
      <span style="text-transform: capitalize">En attente du cours...</span>
    </template>
    <template v-else>
      <br />
      <span
        v-if="!hasStarted && !hasFinished"
        style="background-color: yellow; text-transform: capitalize"
        >{{ kind_str_fr }} Non commencée
        <button v-if="hasPlanningRights && kind_str_fr!='edition'" @click="setStarted()" rel="noopener noreferrer">⏭️<span v-show="loadingCancel || loading" class="loaderr"></span></button>
        <button v-if="hasPlanningRights  && kind_str_fr=='edition'" @click="setStarted();setFinished()" rel="noopener noreferrer">⏭️<span v-show="loadingCancel || loading" class="loaderr"></span></button>
        </span
      >
      <span
        v-else-if="hasStarted && !hasFinished"
        style="background-color: yellow; text-transform: capitalize"
        >{{ kind_str_fr }} En cours
        <button v-if="hasPlanningRights" @click="cancelStarted()" rel="noopener noreferrer">⏮️</button>
        <button v-if="hasPlanningRights" @click="setFinished()" rel="noopener noreferrer">⏭️</button>
        <span v-show="loadingCancel || loading" class="loaderr"></span>
        </span
      >
      <span v-else style="background-color: #90ee90; text-transform: capitalize"
        >{{ kind_str_fr }} Terminée
        <button v-if="hasPlanningRights" @click="cancelFinished()" rel="noopener noreferrer">⏮️<span v-show="loadingCancel || loading" class="loaderr"></span></button>
        </span
      >
    </template>
    <button v-if="canDelete" @click="confirmDelete()" rel="noopener noreferrer">
      ❌
    </button>
  </span>
  <template v-else-if="ts[slot_kind_prise]">Prise 😊</template>
  <template v-else>
    <button @click="showModalAssignOther()" rel="noopener noreferrer" v-if="hasPlanningRights">
      Assigner 
    </button>
    <button @click="showModalThyself()" rel="noopener noreferrer" v-else>
      M'inscrire 🙋‍♀️
    </button>
  </template>
  <!-- <span style="background-color: #f44336; color: white; padding: 3px; text-transform: capitalize" v-else>Désolé, les inscriptions au S2 ne sont pas encore ouvertes...</span> -->
  <!-- <span @click="showModal()" rel="noopener noreferrer" v-else>
    A pourvoir.. 😕
  </span> -->
</template>

<style>
</style>