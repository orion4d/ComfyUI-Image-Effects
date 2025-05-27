import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ImageEffects.CSSFilters",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "CSSFiltersNode") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                
                // Ajouter des styles CSS personnalisés au nœud
                this.addProperty("css_style", "filter-panel", "string");
                
                // Personnaliser l'apparence
                this.color = "#2a4d3a";
                this.bgcolor = "#1a2d2a";
                this.title_text_color = "#ffffff";
                
                // Ajouter une classe CSS personnalisée
                if (this.domElement) {
                    this.domElement.classList.add("css-filters-node");
                }
            };
            
            // Personnaliser l'affichage des widgets
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function (ctx) {
                onDrawForeground?.apply(this, arguments);
                
                // Dessiner un indicateur visuel des filtres actifs
                const activeFilters = this.widgets.filter(w => 
                    w.value !== w.options?.default && w.value !== 0 && w.value !== 100
                ).length;
                
                if (activeFilters > 0) {
                    ctx.fillStyle = "#4CAF50";
                    ctx.fillRect(this.size[0] - 20, 5, 15, 15);
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "10px Arial";
                    ctx.fillText(activeFilters.toString(), this.size[0] - 17, 15);
                }
            };
        }
    }
});
