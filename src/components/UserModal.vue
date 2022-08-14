<template>
  <Modal ref="modalName">
    <template v-slot:header>
      <h1>Fiche membre de : {{firstname}} {{lastname}}</h1>
    </template>

    <template v-slot:body>

      <h2>{{erasmus}}</h2>
      <h2>{{demission}}</h2>
      <h2>{{droits}}</h2>


      <h2>Infos modifiables :</h2>
      <div class="inputfield">
        <label for="erasmus">Erasmus ?</label>
        <input type="checkbox" id="erasmus" v-model="erasmus">
      </div>
      <div class="inputfield">
        <label for="demission">Démission ?</label>
        <input type="checkbox" id="demission" v-model="demission">
      </div>
      <div class="inputfield">
        <label for="droits">Droits ?</label>
        <select name="droits" id="droits" v-model="droits">
          <option value="membre">Membre Actif</option>
          <option value="edition">Admin Édition</option>
          <option value="planning">Admin Planning</option>
          <option value="recrutement">Admin Recrutement</option>
          <option value="presidence">Présidence</option>
        </select>
      </div>

      <br/>

      <h2>Créneaux choisis (même annulés, hors édition) :</h2>
      <h3>
        <em
          >Remarque : Pour information les créneaux et les noms des autres membres
          de l'APECS du même horaire sont indiqués</em
        >
      </h3>
      <Planning v-if="!hasNoData" :horaires="horaires" />
      <h2 v-else>N'a pas pris de créneau pour le moment.</h2>
    </template>

    <template v-slot:footer>
      <div class="buttons">
        <button class="btn-red" @click="$refs.modalName.close">Annuler</button>
        <button class="btn-green" @click="register" :disabled="loading">
          <span v-show="loading" class="loaderr"></span>
          <span>Mettre à jour cette fiche membre</span>
        </button>
      </div>
    </template>
  </Modal>
</template>

<script>
import Modal from "./Modal";
import Planning from "../components/Planning.vue";
import { Http } from "@capacitor-community/http";
export default {
  components: {
    Modal,
    Planning,
  },
  props: {
    mail: String,
    firstname: String,
    lastname: String,
    settings: String,
  },
  data() {
    return {
      horaires: [],
      erasmus: false,
      demission: true,
      droits: "membre",
    };
  },
  watch: {
    h: [
      {
        handler: "geth_wuser",
      },
    ],
  },
  mounted() {
    this.refreshUserPlanning();
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

      var user_self_inscript_id = 2;
      // const requestOptions = {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({
      //     user_assigned: user_self_inscript_id,
      //     user_modif: user_self_inscript_id,
      //     reason: "Self-inscript",
      //     timestamp_start: this.ts.s_begin,
      //     timestamp_end: this.ts.s_end,
      //     class_id: this.h.class_id,
      //     timeslot_kind: this.kind,
      //   }),
      // };
      // fetch(this.$API_URL + "/registerRoneoD1", requestOptions)
      //   .then((response) => response.json())
      //   // .then((data) => console.log(data))
      //   .then(() => {
      //     this.$refs.modalName.close();
      //     this.$emit("refresh");
      //   });
      const body = {
        user_assigned: user_self_inscript_id,
        user_modif: user_self_inscript_id,
        reason: "Self-inscript",
        timestamp_start: this.ts.s_begin,
        timestamp_end: this.ts.s_end,
        class_id: this.h.class_id,
        timeslot_kind: this.kind,
      };
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/registerRoneoD1",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: body,
      }).then(() => {
          this.loading = false;
          this.$emit("refresh");
          this.$refs.modalName.close();
        });
    },
    async refreshUserPlanning() {
      this.horaires = [];

      await Http.request({
        method: "POST",
        url: this.$API_URL + "/planningForUserMail",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {
          "mail": this.mail
        }
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