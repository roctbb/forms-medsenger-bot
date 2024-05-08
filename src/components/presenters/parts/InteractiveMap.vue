<template>
    <div v-if="map" style="margin: 5px">
        <human-map v-if="map == 'human'" :parts="parts" :uid="uid"/>
        <child-map v-if="map == 'child'" :parts="parts" :uid="uid"/>
        <emotions-map v-if="map == 'emotions'" :parts="parts" :uid="uid"/>
        <yes-no-map v-if="map == 'yes_no'" :parts="parts" :uid="uid"/>
        <emoji-map v-if="map == 'emoji'" :parts="parts" :uid="uid"/>

        <br>

        <div v-if="!is_map_preview">
            <b>Выбор:</b> <i>{{ parts.length ? parts.join(', ') : 'Ничего не выбрано' }}</i>
        </div>
    </div>
</template>

<script>

import HumanMap from "../../maps/human/HumanMap";
import ChildMap from "../../maps/child/ChildMap";
import EmotionsMap from "../../maps/emotions/EmotionsMap.vue";
import YesNoMap from "../../maps/yes-no/YesNoMap.vue";
import EmojiMap from "../../maps/emoji/EmojiMap.vue";

export default {
    name: "InteractiveMap",
    components: {EmojiMap, YesNoMap, EmotionsMap, HumanMap, ChildMap},
    props: ['map', 'uid', 'is_map_preview', 'disabled'],
    data() {
        return {
            parts: [],
        }
    },
    computed: {},
    created() {
        Event.listen('mouse-down', (data) => {
            if (this.disabled || data.uid !== this.uid) return
            let part = this.parts.filter(p => p == data.zone)
            if (part.length)
                this.parts = this.parts.filter(p => p != data.zone)
            else
                this.parts.push(data.zone)

            if (!this.is_map_preview)
                Event.fire('interactive-map-answer', {answer: this.parts, uid: this.uid})
        })

        Event.listen('set-map-zones', (data) => {
            if (data.uid !== this.uid) return
            this.parts = data.parts
            this.$forceUpdate()
        })
    }
}
</script>

<style>
@media (hover: hover) and (pointer: fine) {
    path.part:hover {
        stroke: #000000 !important;
        stroke-width: 1px;
        stroke-linejoin: round;
        cursor: pointer;
    }
}

#info-box {
    display: none;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
    background-color: #ffffff;
    border: 2px solid #006c88;
    border-radius: 5px;
    padding: 5px;
}
</style>
