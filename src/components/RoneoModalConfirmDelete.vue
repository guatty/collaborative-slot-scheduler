<template>
  <Modal ref="modalConfirmDelete">
    <template v-slot:header>
      <h1>Suppression d'un horaire</h1>
    </template>

    <template v-slot:body>
      <p>
        Rôle : <b style="text-transform: capitalize">{{ kind }}</b>
      </p>
      <p>
        Créneau de
        <b>
          {{ this.$tsHm(h.h_debut + ts.s_begin) }} à
          {{ this.$tsHm(h.h_debut + ts.s_end) }}
        </b>
      </p>
      <p>
        <em>Rappel de l'horaire sélectionné :</em>
        <span class="hdate">{{ $filters.date_to_fr(h.h_date) }}</span>
        <ClassCard v-if="ishwuloaded" v-bind:h="h_wusers" class="disabled" />
        <span v-else class="loaderr"></span>
      </p>
    </template>

    <template v-slot:footer>
      <div class="buttons">
        <button class="btn-red" @click="$refs.modalConfirmDelete.close">Annuler</button>
        <button class="btn-green" @click="register" :disabled="loading">
          <span v-show="loading" class="loaderr"></span>
          <span>Je supprime ce créneau de {{ kind }}</span>
        </button>
      </div>
    </template>
  </Modal>
</template>

<script>
import Modal from "./Modal";
import ClassCard from "./ClassCard";
import { Http } from "@capacitor-community/http";
export default {
  components: {
    Modal,
    ClassCard,
  },
  props: {
    h: Object,
    ts: Object,
    kind: Object,
  },
  data() {
    return {
      loading: false,
      h_wusers: {},
      ishwuloaded: false,
    };
  },
  watch: {
    h: [
      {
        handler: "geth_wuser",
      },
    ],
  },
  methods: {
    async geth_wuser(el) {
      this.ishwuloaded = false;
      const body = {
        class_id: el.class_id,
      };
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/classInfo",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: body,
      }).then(({ data }) => {
          this.h_wusers = data;
          this.ishwuloaded = true;
        });
    },
    async register() {
      this.loading = true;

      const body = {
        reason: "Suppression créneau",
        timestamp_start: this.ts.s_begin,
        timestamp_end: this.ts.s_end,
        class_id: this.h.class_id,
        timeslot_kind: this.kind,
      };
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/confirmCancelCreneauPlanning",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: body,
      })
        .then(() => {
          this.loading = false;
          this.$emit("refresh");
          this.$refs.modalConfirmDelete.close();
        });
    },
  },
};
</script>

<style>
h1 {
  display: flex;
  align-items: center;
  text-align: center;
}
.buttons {
  display: flex;
  justify-content: space-evenly;
}
.disabled button {
  visibility: hidden;
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
}
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
</style>