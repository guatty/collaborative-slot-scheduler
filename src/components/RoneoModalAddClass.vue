<template>
  <Modal ref="modalName">
    <template v-slot:header>
      <h1>Ajout d'un nouveau cours</h1>
    </template>

    <template v-slot:body>
      <label for="amphi">Amphi :</label>
      <input id="amphi" v-model="amphi" placeholder="400"><br/>

      <label for="ens">Enseignant :</label>
      <input id="ens" v-model="ens"><br/>

      <label for="date_time">Date et heure du cours :</label>
      <Datepicker id="date_time" v-model="date_time" locale="fr" :format-locale="fr" :minTime="{ hours: 0, minutes: 30 }" /><br/>

      <label for="duree_hms">Durée (arrondie à la demi-heure près) :</label>
      <Datepicker id="duree_hms" v-model="duree_hms" timePicker minutesIncrement="30" :minTime="{ hours: 0, minutes: 30 }" /><br/>

      <label for="intitule">Titre du cours :</label>
      <textarea id="intitule" v-model="intitule" rows="4" cols="50"/><br/>

      <label for="reason">Commentaire / raison de cet ajout de cours :</label>
      <textarea id="reason" v-model="reason" rows="4" cols="50"/><br/>
      
      <label for="num_ue">Numéro de l'UE :</label>
      <input type="number" id="num_ue" v-model="num_ue" min="1" max="14"><br/>
      
    </template>

    <template v-slot:footer>
      <div class="buttons">
        <button class="btn-red" @click="$refs.modalName.close">Annuler</button>
        <button class="btn-green" @click="register" :disabled="loading">
          <span v-show="loading" class="loaderr"></span>
          <span>J'ajoute un nouveau cours</span>
        </button>
      </div>
    </template>
  </Modal>
</template>

<script>
import Modal from "./Modal";
import { Http } from "@capacitor-community/http";
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
export default {
  components: {
    Modal, Datepicker
  },
  props: {
    h: Object,
    ts: Object,
    kind: Object,
  },
  data() {
    return {
      loading: false,
      amphi: "",
      ens: "",
      date_time: "",
      duree_hms: { "hours": 1, "minutes": 0, "seconds": 0 },
      intitule: "",
      num_ue: "",
      reason: "Nouveau cours sur le planning."
    };
  },
  methods: {
    async register() {
      this.loading = true;
      const body = {
        reason: this.reason,
        amphi: this.amphi,
        ens: this.ens,
        date_time: this.date_time.setHours(this.date_time.getHours() + 1) / 1000,
        duree_sec: this.duree_hms.hours*3600 + this.duree_hms.minutes*60 + this.duree_hms.seconds,
        intitule: this.intitule,
        num_ue: this.num_ue,
      };
      console.log(body)
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/addClass",
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