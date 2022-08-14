<template>
  <div id="vmsd">
    <button @click="isModalAddClassVisible=true" rel="noopener noreferrer" v-if="hasPlanningRights">
      ➕ 
    </button>
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

  <RoneoModalAddClass
    ref="modalAddClass"
    v-show="isModalAddClassVisible"
    @closeModal="closeModal"
    @refresh="transmitRefresh"
  />
</template>

<script>
import Planning from "./Planning.vue";
import VueMultiselect from "vue-multiselect";
import { Http } from "@capacitor-community/http";
import RoneoModalAddClass from "./RoneoModalAddClass.vue";
export default {
  components: { Planning, VueMultiselect, RoneoModalAddClass },
  data() {
    return {
      isModalAddClassVisible: false,
      hasPlanningRights: false,
      horaires: [],
      selected: [
        { name: "Afficher uniquement à partir d'aujourd'hui", categorie: "", h_type: "", restreinte: "hodiaux" },
        { name: "Cours / séances de sémiologie", categorie: "", h_type: "semio" },
        { name: "UE 13 - Appareil digestif", categorie:"UE13", h_type: ""},
        { name: "UE 14 - Nutrition", categorie:"UE14", h_type: ""},
      ],
      loading: true,
      options: [
        {
          ng: "UE S2",
          cat: [
            { name: "UE 8 - Sémiologie générale", categorie:"UE8", h_type: ""},
            { name: "UE 9 - Bases moléculaires et cellulaires des pathologies", categorie:"UE9", h_type: ""},
            { name: "UE 11 - Hormonologie – reproduction", categorie:"UE11", h_type: ""},
            { name: "UE 12 - Revêtement cutané", categorie:"UE12", h_type: ""},
            { name: "UE 13 - Appareil digestif", categorie:"UE13", h_type: ""},
            { name: "UE 14 - Nutrition", categorie:"UE14", h_type: ""},
          ],
        },
        {
          ng: "Autres",
          cat: [
            { name: "Cours / séances de sémiologie", categorie: "", h_type: "semio" },
            { name: "Examens & Rattrapages", categorie: "examen", h_type: "" },
            { name: "Présentations", categorie: "Pres", h_type: "" },
            { name: "N'afficher que les CM", categorie: "", h_type: "", restreinte: "CM" },
            { name: "Afficher uniquement à partir d'aujourd'hui", categorie: "", h_type: "", restreinte: "hodiaux" },
          ],
        },
        {
          ng: "Restreindre par période",
          cat: [
            { name: "S1 (jusqu'au 11 fév.)", categorie: "", h_type: "", restreinte: "S1" },
            { name: "S2 (à partir du 21 fév.)", categorie: "", h_type: "", restreinte: "S2" },
          ],
        },
        {
          ng: "UE S1",
          cat: [
            { name: "UE 1 - Biopathologies tissulaires, illustrations et moyens d’exploration", categorie:"UE1", h_type: ""},
            { name: "UE 2 - Bases moléculaires, cellulaires et tissulaires des traitements médicamenteux", categorie:"UE2", h_type: ""},
            { name: "UE 3 - Tissu sanguin et système immunitaire", categorie:"UE3", h_type: ""},
            { name: "UE 4 - Appareil respiratoire", categorie:"UE4", h_type: ""},
            { name: "UE 5 - Système cardiovasculaire", categorie:"UE5", h_type: ""},
            { name: "UE 6 - Agents infectieux", categorie:"UE6", h_type: ""},
            { name: "UE 7 - Informatique médicale", categorie:"UE7", h_type: ""},
          ],
        },
      ],
    };
  },
  mounted() {
    this.hasPlanningRights = this.$store.getters["auth/hasPlanningRights"];
    this.refreshPlanning();
  },
  methods: {
    closeModal() {
      this.isModalAddClassVisible = false;
    },
    async refreshPlanning() {
      this.horaires = [];
      this.loading = true;
      var urlll = this.$store.getters["auth/isAuthenticatedEvenIfExpired"] ? "gestion" : "";
      await Http.request({
        method: "POST",
        url: this.$API_URL + "/planningP2" + urlll,
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