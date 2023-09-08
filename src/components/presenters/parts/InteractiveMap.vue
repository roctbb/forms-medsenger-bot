<template>
    <div v-if="map" style="margin: 5px">
        <human-map v-if="map == 'human'" :parts="parts" />
        <child-map v-if="map == 'child'" :parts="parts" />
    </div>
</template>

<script>

import HumanMap from "../../maps/human/HumanMap";
import ChildMap from "../../maps/child/ChildMap";

export default {
    name: "InteractiveMap",
    components: {HumanMap,ChildMap},
    props: ['map', 'uid'],
    data() {
        return {
            parts: [],
        }
    },
    computed: {
    },
    created() {
        Event.listen('mouse-down', zone => {
            let part = this.parts.filter(p => p == zone)
            if (part.length)
                this.parts = this.parts.filter(p => p != zone)
            else
                this.parts.push(zone)

            if (this.uid)
                Event.fire('interactive-map-answer', {answer: this.parts, uid: this.uid})
        })
    }
}
</script>

<style>
@media (hover: hover) and (pointer: fine) {
    path:hover, circle:hover {
        stroke: #24a8b4 !important;
        stroke-width: 1px;
        stroke-linejoin: round;
        fill: #24a8b4 !important;
        cursor: pointer;
    }
}

#info-box {
    display: none;
    position: absolute;
    top: 0px;
    left: 0px;
    z-index: 1;
    background-color: #ffffff;
    border: 2px solid #006c88;
    border-radius: 5px;
    padding: 5px;
}
</style>
