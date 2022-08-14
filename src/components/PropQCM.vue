<script>
export default {
  props: {
    prop: Object,
    dispCorrection: Boolean,
  },
  data() {
    return {
      inputValue: null,
    };
  },
  computed: {
    isRight() {
      return (
        (this.inputValue == "true" && this.prop.value) ||
        (this.inputValue == "false" && !this.prop.value)
      );
    },
    isWrong() {
      return (
        (this.inputValue == "true" && !this.prop.value) ||
        (this.inputValue == "false" && this.prop.value)
      );
    },
    hasCorrectionRight(){
      return this.$store.getters["auth/hasCorrectionRight"];
    }
  },
  methods: {
    toggleInputValue(value) {
      this.inputValue = value;
      this.$emit('inputChanged', this.isRight);
    }
  }
};
</script>

<template>
  <div class="proposition">
    <div class="item">
      <span>{{ prop.id }}</span>
    </div>
    <div class="item item-center">{{ prop.content }}</div>
    <div class="corrvaluet">
      <div class="item both">
        <span
          class="true"
          :class="{
            trueSelected:
              (prop.value && dispCorrection) ||
              (inputValue == 'true' && !dispCorrection),
          }"
          :onClick="() => toggleInputValue('true')"
          >Vrai</span
        >
        <!-- <hr style="width:60%;flex-grow:0;"> -->
        <span
          class="false"
          :class="{
            falseSelected:
              (!prop.value && dispCorrection) ||
              (inputValue == 'false' && !dispCorrection),
          }"
          :onClick="() => toggleInputValue('false')"
          >Faux</span
        >
      </div>
      <div class="corrvalue" v-if="dispCorrection">
        <span v-if="isRight">✅</span>
        <span v-else-if="isWrong">❌</span>
        <span v-else>❔</span>
      </div>
    </div>
  </div>

  <div class="correction" v-if="dispCorrection && hasCorrectionRight" >
    <span class="item">Correction : </span>
    <img class="item item-img" :src="prop.img" v-if="prop.img" />
    <span class="item item-center">{{ prop.correction }}</span>
  </div>
</template>

<style>
.proposition {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  margin: 5px;
  background-color: white;
  align-items: stretch;
}
.corrvaluet {
  display: flex;
  flex-direction: row;
  width: 100px; /* A fixed width as the default */
  display: flex;
  justify-content: center;
  vertical-align: middle;
}
.both {
  background-color: lightgray;
  display: flex;
  flex-direction: column;
  justify-content: center;
  vertical-align: middle;
  min-height: 5em;
  min-width: 5em;
}
.trueSelected {
  background-color: lightgreen;
}
.falseSelected {
  background-color: lightcoral;
}
.true,
.false {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  vertical-align: middle;
}

.item {
  width: 100px; /* A fixed width as the default */
  display: flex;
  flex-direction: column;
  justify-content: center;
  vertical-align: middle;
}

.item-center {
  flex-grow: 1; /* Set the middle element to grow and stretch */
  padding-block: 5px;
}

.item-img {
  width: auto;
  max-height: 100%;
}

.item + .item {
  margin-left: 2%;
}

.correction {
  margin-bottom: 1em;
  background-color: lightgreen;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  margin: 5px;
  align-items: stretch;
}
.correction span {
  vertical-align: text-bottom;
}
.corrvalue {
  background-color: #00afef;
  width: 5em;
  font-size: 3em;
  display: flex;
  flex-direction: column;
  justify-content: center;
  vertical-align: middle;
}

@media screen and (max-width: 600px) {
  .proposition {
    margin: 2px;
    margin-block: 3px;
  }
  .corrvaluet {
    width: 100px; /* A fixed width as the default */
  }
  .both {
    min-height: 2em;
    min-width: 2em;
  }

  .item {
    width: 100px; /* A fixed width as the default */
  }

  .item-img {
    width: auto;
    max-height: 100%;
  }

  .item + .item {
    margin-left: 0%;
  }

  .correction {
    margin: 0px;
    margin-bottom: 5px;
  }
  .corrvalue {
    width: 2em;
  }
}
</style>