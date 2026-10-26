import { app } from "/scripts/app.js";

const USER_DEFINED = "Custom > user defined";

function setWidgetVisible(node, widget, visible) {
    if (visible) {
        if (widget.origType !== undefined) {
            widget.type = widget.origType;
            widget.computeSize = widget.origComputeSize;
            delete widget.origType;
        }
    } else if (widget.origType === undefined) {
        widget.origType = widget.type;
        widget.origComputeSize = widget.computeSize;
        widget.type = "hidden";
        widget.computeSize = () => [0, -4];
    }
    if (widget.element) widget.element.style.display = visible ? "" : "none";
    node.setSize([node.size[0], node.computeSize()[1]]);
    app.graph.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "pinkpixel.prompt_enhancer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "PromptEnhancer") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

            const styleWidget = this.widgets.find(w => w.name === "style");
            const customWidget = this.widgets.find(w => w.name === "custom_style");
            if (!styleWidget || !customWidget) return r;

            const update = () => setWidgetVisible(this, customWidget, styleWidget.value === USER_DEFINED);
            const callback = styleWidget.callback;
            styleWidget.callback = function () {
                const res = callback ? callback.apply(this, arguments) : undefined;
                update();
                return res;
            };
            update();
            return r;
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const r = onConfigure ? onConfigure.apply(this, arguments) : undefined;
            const styleWidget = this.widgets.find(w => w.name === "style");
            const customWidget = this.widgets.find(w => w.name === "custom_style");
            if (styleWidget && customWidget) setWidgetVisible(this, customWidget, styleWidget.value === USER_DEFINED);
            return r;
        };
    }
});
