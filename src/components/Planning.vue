<template>
  <div class="planning">
    <div class="phead">
      <div>
        Planning tiré du PDF reçu de la scolarité : Attention aux changements !
      </div>
    </div>
    <div class="planning_data" v-if="horaires.length">
      <div class="semaine" v-for="week in horaires" :key="week.week_number">
            <PlanningWeek 
                v-bind:week="week"
              @showModal="showModal"
              @showModalAssignOther="showModalAssignOther"
              @showModalConfirmDelete="showModalConfirmDelete"
              @showModalEditClass="showModalEditClass"
              v-bind="$attrs" 
            />
      </div>
    </div>
    <div v-else-if="loaded" class="placeholderloading">
      Aucun créneau à afficher. <br>Veuillez revoir vos catégories sélectionnées...
    </div>
    <div v-else class="placeholderloading">
      Chargement du planning en cours....<br />Veuillez patienter...
    </div>
  </div>
  <RoneoModal
    ref="modalName"
    v-show="isModalVisible"
    @closeModal="closeModal"
    v-bind="modalModel"
    @refresh="transmitRefresh"
  />
  <RoneoModalConfirmDelete
    ref="modalConfirmDelete"
    v-show="isModalConfirmDeleteVisible"
    @closeModal="closeModal"
    v-bind="modalModel"
    @refresh="transmitRefresh"
  />
  <RoneoModalAssignOther
    ref="modalAssignOther"
    v-show="isModalAssignOtherVisible"
    @closeModal="closeModal"
    v-bind="modalModel"
    @refresh="transmitRefresh"
  />
  <RoneoModalEditClass
    ref="modalEditClass"
    v-show="isModalEditClassVisible"
    @closeModal="closeModal"
    v-bind="modalEditClassModel"
    @refresh="transmitRefresh"
  />
</template>

<script>
import RoneoModal from "./RoneoModal.vue";
import PlanningWeek from "./PlanningWeek.vue";
import RoneoModalConfirmDelete from "./RoneoModalConfirmDelete.vue";
import RoneoModalAssignOther from "./RoneoModalAssignOther.vue";
import RoneoModalEditClass from "./RoneoModalEditClass.vue";
export default {
  components: { RoneoModal, RoneoModalConfirmDelete, RoneoModalAssignOther, RoneoModalEditClass, PlanningWeek },
  data() {
    return {
      isModalVisible: false,
      isModalConfirmDeleteVisible: false,
      isModalAssignOtherVisible: false,
      isModalEditClassVisible: false,
      modalModel: {
        h: Object,
        ts: Object,
        kind: String,
      },
      modalEditClassModel: {}
    };
  },
  props: { horaires: Array, loaded: Boolean },
  methods: {
    showModal(info) {
      this.modalModel = info;
      this.isModalVisible = true;
    },
    showModalAssignOther(info) {
      this.modalModel = info;
      this.isModalAssignOtherVisible = true;
    },
    showModalConfirmDelete(info) {
      this.modalModel = info;
      this.isModalConfirmDeleteVisible = true;
    },
    showModalEditClass(info) {
      this.modalEditClassModel = info;
      this.isModalEditClassVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
      this.isModalAssignOtherVisible = false;
      this.isModalConfirmDeleteVisible = false;
      this.isModalEditClassVisible = false;
    },
    transmitRefresh() {
      this.$emit("refresh");
    },
  },
};
</script>

<style>
.planning {
  /* box-shadow: 0 1px 10px #000000; */
  margin-inline: 0;
  max-width: 1200px;
  display: inline-block;
  box-shadow: -1em 0 0.4em #75b9f9, 6px 0 #facf51;
}
.phead {
  background-color: #00afef;
  position: sticky;
  top: 0px;
  padding: 0.3em;
  font-weight: bold;
  color: white;
  /* text-shadow: 2px 0 0 #fff, -2px 0 0 #fff, 0 2px 0 #fff, 0 -2px 0 #fff, 1px 1px #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff; */
  text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;
}
.weekHeader {
  font-weight: bold;
  border-radius: 4px;
  color: black;
  background: #ffff00;
  margin-inline: 4em;
  padding: 1.4em;
}
.semaine {
  background-color: black;
}
.weekDay {
  display: flex;
  flex-direction: column;
  margin-block: 0.5em;
  text-align: center;
  justify-content: flex-start;
  overflow-x: auto;
}
.classesOfTheDay {
  display: flex;
  flex-direction: column;
  background-color: lightgray;
}
.hdate {
  display: flex;
  overflow: hidden;
  flex-grow: 1;
  flex-shrink: 0;
  font-weight: bolder;
  border-radius: 18px 75% 0 0;
  color: #efff08;
  background: #00afef;
  padding-block: 0.5em;
  padding-inline: 4em;
  text-shadow: -1px 0 black, 0 1px #000000, 1px 0 black, 0 -1px black;
  text-transform: capitalize;
}
.planning_data {
  /* display: flex; */
  align-items: center;
  /* flex-direction: column; */
}
.placeholderloading {
  font-weight: bolder;
  background-color: #ffff00;
}
body {
  margin-inline: 0;
}
</style>