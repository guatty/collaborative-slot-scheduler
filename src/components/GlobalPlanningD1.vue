<template>
  <div id="vmsd">
    <VueMultiselect
      id="vms"
      v-model="selected"
      :options="options"
      group-values="cat"
      group-label="ng"
      :multiple="true"
      :searchable="true"
      :hideSelected="true"
      placeholder="Afficher uniquement les catégories sélectionnées..."
      :selectLabel="''"
      :deselectLabel="''"
      :selectGroupLabel="'Cliquez pour tout ajouter'"
      :deselectGroupLabel="'Cliquez pour tout retirer'"
      :loading="loading"
      :showNoResults="false"
      :group-select="true"
      :max-height="10000"
      track-by="name"
      label="name"
    >
    </VueMultiselect>

    <button class="buttonwithloader" :disabled="loading" @click="refreshPlanning()" rel="noopener noreferrer">✅</button>
  </div>
  <Planning :horaires="horaires" @refresh="refreshPlanning" v-bind="$attrs" :loaded="!loading" />
</template>

<script>
import Planning from "./Planning.vue";
import VueMultiselect from "vue-multiselect";
import { Http } from "@capacitor-community/http";
export default {
  components: { Planning, VueMultiselect },
  data() {
    return {
      horaires: [],
      selected: [
        { name: "N'afficher que les CM", categorie: "", h_type: "", restreinte: "CM" },
        { name: "Microbiologie", categorie: "MB", h_type: "" },
      ],
      loading: true,
      options: [
        {
          ng: "UE",
          cat: [
            { name: "UE 1 (CM & TD JDR)", categorie:"UE1", h_type: ""},
            { name: "UE 2 (CM)", categorie:"UE2", h_type: ""},
            { name: "UE 3 (CM & TP pharma/histo/anat)", categorie:"UE3", h_type: ""},
            { name: "UE 4 (CM)", categorie:"UE4", h_type: ""},
            { name: "UE 5 (CM & TP anat 1&2)", categorie:"UE5", h_type: ""},
            { name: "UE 6 (CM & TP anat/physio)", categorie:"UE6", h_type: ""},
            { name: "UE 7 (CM & ED)", categorie:"UE7", h_type: ""},
            { name: "UE 8: Biostatistiques (CM)", categorie:"UE8:Biostat", h_type: ""},
            { name: "UE 8: LCA (CM)", categorie:"UE8:LCA", h_type: ""},
          ],
        },
        {
          ng: "Autres",
          cat: [
            { name: "AFGSU", categorie: "AFGSU", h_type: "" },
            { name: "Cas Cliniques", categorie: "CasClin", h_type: "" },
            { name: "Controles Continues", categorie: "CC", h_type: "" },
            { name: "CUESIM", categorie: "CUESIM", h_type: "" },
            { name: "ECOS", categorie: "ECOS", h_type: "" },
            { name: "Examens & Rattrapages", categorie: "examen", h_type: "" },
            { name: "Présentations", categorie: "Pres", h_type: "" },
            { name: "TP d'Urgences Vitales", categorie: "UrgVit", h_type: "" },
            { name: "SSES / SESA", categorie: "SSES", h_type: "" },
            { name: "N'afficher que les CM", categorie: "", h_type: "", restreinte: "CM" },
            { name: "Afficher uniquement à partir d'aujourd'hui", categorie: "", h_type: "", restreinte: "hodiaux" },
          ],
        },
        {
          ng: "Restreindre par période",
          cat: [
            { name: "S1 (jusqu'au 18 nov.)", categorie: "", h_type: "", restreinte: "S1" },
            { name: "S2 (du 19 nov. au 9 mars)", categorie: "", h_type: "", restreinte: "S2" },
            { name: "FASM (à partir du 10 mars)", categorie: "", h_type: "", restreinte: "FASM1" },
          ],
        },
        {
          ng: "FASM 1",
          cat: [
            { name: "Microbiologie", categorie: "MB", h_type: "" },
            { name: "Maladies Infectieuses", categorie: "MI", h_type: "" },
            { name: "Ophtalmologie", categorie: "Ophtalmologie", h_type: "" },
          ],
        },
        {
          ng: "Stage de sémiologie",
          cat: [
            { name: "Sémio: 1ère période", categorie: "StageSemio", h_type: "StageSemio:T1" },
            { name: "Sémio: 2ème période", categorie: "StageSemio", h_type: "StageSemio:T2" },
            { name: "Sémio: 3ème période", categorie: "StageSemio", h_type: "StageSemio:T3" },
          ],
        },
        {
          ng: "TD Jeu de Rôle UE 1",
          cat: [
            { name: "TD Jeu de Rôle Groupe 1", categorie: "UE1", h_type: "TD:JDR:G1" },
            { name: "TD Jeu de Rôle Groupe 2", categorie: "UE1", h_type: "TD:JDR:G2" },
            { name: "TD Jeu de Rôle Groupe 3", categorie: "UE1", h_type: "TD:JDR:G3" },
            { name: "TD Jeu de Rôle Groupe 4", categorie: "UE1", h_type: "TD:JDR:G4" },
          ],
        },
        {
          ng: "TP / ED : catégories",
          cat: [
            { name: "UE 3 : ED Pharmaco", categorie: "UE3", h_type: "ED:Pharmaco" },
            { name: "UE 3 : TP Anatomie", categorie: "UE3", h_type: "TP:AnatomieUE3.1" },
            { name: "UE 3 : TP Histologie", categorie: "UE3", h_type: "TP:Histologie" },
            { name: "UE 5 : TP Anatomie #1", categorie: "UE5", h_type: "TP:AnatomieUE5.1" },
            { name: "UE 5 : TP Anatomie #2", categorie: "UE5", h_type: "TP:AnatomieUE5.2" },
            { name: "UE 6 : TP Anatomie", categorie: "UE6", h_type: "TP:AnatomieUE6.1" },
            { name: "UE 6 : TP Physiologie (Promo entière)", categorie: "UE6", h_type: "TP:Physiologie" },
            { name: "UE 7 : ED Génétique", categorie: "UE7", h_type: "ED:Genetique.1" },
            { name: "TP Biophysique sensorielle : Vision", categorie: "TP:BioSens.1", h_type: "TP:BioSens.1" },
            { name: "TP Biophysique sensorielle : Audition", categorie: "TP:BioSens.1", h_type: "TP:BioSens.2" },
          ],
        },
        {
          ng: "TP / ED : Restreindre aux groupes",
          cat: [
            { name: "Groupe 1", categorie: "", h_type: ":G1" },
            { name: "Groupe 2", categorie: "", h_type: ":G2" },
            { name: "Groupe 3", categorie: "", h_type: ":G3" },
            { name: "Groupe 4", categorie: "", h_type: ":G4" },
            { name: "Groupe 5", categorie: "", h_type: ":G5" },
            { name: "Groupe 6", categorie: "", h_type: ":G6" },
            { name: "Groupe 7", categorie: "", h_type: ":G7" },
            { name: "Groupe 8", categorie: "", h_type: ":G8" },
            { name: "Groupe 9", categorie: "", h_type: ":G9" },
            { name: "Groupe 10", categorie: "", h_type: ":G10" },
            { name: "Groupe 11", categorie: "", h_type: ":G11" },
            { name: "Groupe 12", categorie: "", h_type: ":G12" },
          ],
        },
      ],
    };
  },
  mounted() {
    this.refreshPlanning();
  },
  methods: {
    async refreshPlanning() {
      this.horaires = [];
      this.loading = true;
      var urlll = this.$store.getters["auth/isAuthenticatedEvenIfExpired"] ? "gestion" : "";
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/planningD1" + urlll,
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: this.selected,

      })
        .then(({ data }) => {
          this.horaires = data;
          this.loading = false;
        })
        .catch((err) => console.log(err));
      // fetch(this.$API_URL + "/planningD1")
      //   .then((res) => res.json())
      //   .then((data) => (this.horaires = data))
      //   .catch((err) => console.log(err));
    },
  },
};
</script>

<style src="vue-multiselect/dist/vue-multiselect.css">
</style>
<style>
#vmsd {
  display: flex;
  padding-inline: 20px;
  margin-left: auto;
  margin-right: auto;
  flex-direction: row;
  justify-content: center;
  margin-bottom: 5px;
  max-width: 800px;
}
</style>