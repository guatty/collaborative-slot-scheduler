<template>
  <div class="classRoneo">
    <template v-if="h.timeslots">
      <div class="roneoTimeSlot" v-for="ts in h.timeslots" :key="ts.slot_id">
        <span v-if="h.timeslots.length >= 2">#{{ ts.slot_id }}</span>

        <span v-if="ts.edition_finished!=null">
                <span style="background-color: #90ee90; text-transform: capitalize">Le cours est disponible sur le Drive 😊</span>
        </span>
        <span v-else-if="ts.edition_started!=null">
                <span style="background-color: yellow; text-transform: capitalize">Le cours sera bientôt mis en page 😊</span>
        </span>
        <div class="scribeAndRelecture" v-if="(ts.edition_finished==null & ts.edition_started==null) | hasEditionRights">
          <span v-bind:class="{slot_taken: ts.scribe_prise}" v-if="ts.chercheScribe | ts.scribe_prise">
            <span class="creneauScribe">Transcription : </span>
            <SlotTask :kind_obj="ts.scribe" :kind_str_fr=" 'scribe' " :kind_str_en=" 'scribe' " :ts="ts" :h="h" v-bind="$attrs" />
          </span>
          <hr style="width:70%;">
          <span v-bind:class="{slot_taken: ts.relecture_prise}" v-if="ts.chercheRelecture | ts.relecture_prise">
            <span class="creneauRelecture">Relecture : </span>
            <SlotTask :kind_obj="ts.proofread" :kind_str_fr=" 'relecture' " :kind_str_en=" 'proofread' " :ts="ts" :h="h" v-bind="$attrs" />
          </span>
          <hr style="width:70%;" v-if="hasEditionRights">
          <span v-bind:class="{slot_taken: ts.edition_prise}" v-if="hasEditionRights">
            <span class="creneauRelecture">Edition : </span>
            <SlotTask :kind_obj="ts.edition" :kind_str_fr=" 'edition' " :kind_str_en=" 'edition' " :ts="ts" :h="h" v-bind="$attrs" />
          </span>
        </div>
        <!-- <span>⏳</span> -->
      </div>
    </template>
    <template v-else>{{ h.nonRetranscritRaison }}</template>
  </div>
</template>


<script>
import SlotTask from "./SlotTask";
export default {
  components: {
    SlotTask,
  },
  props: {
    h: Object,
    customSRmessage: Object,
  },
  computed: {
      hasEditionRights() { return this.$store.getters["auth/hasEditionRights"] },
  },
};
</script>


<style>
.classRoneo {
  display: flex;
  flex-direction: column;
  width: 45%;
  justify-content: center;
  background-color: darkgray;
}
.roneoTimeSlot {
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
}
.classRoneo > *:not(:last-child) {
  margin-bottom: 0.4em;
}
.classRoneo > * {
  background-color: lightyellow;
  height: 100%;
}
.roneoTimeSlot > span {
  padding: 0.2em;
  display: flex;
  justify-content: center;
  flex-direction: column;
  justify-content: space-evenly;
}
.scribeAndRelecture {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
}
.slot_taken {
  background-color: #90ee90;
}
</style>