document.addEventListener("DOMContentLoaded", function () {
    // Busca todos os selects da página (tanto o do form quanto o do gráfico)
    const selects = document.querySelectorAll("#moeda-form, #moeda, #periodo");

    selects.forEach(select => {
        // 1. Cria o container principal do custom select
        const container = document.createElement("div");
        container.classList.add("custom-select-container");
        select.parentNode.insertBefore(container, select);
        container.appendChild(select);

        // 2. Cria o elemento que exibe a opção selecionada atual
        const styledSelect = document.createElement("div");
        styledSelect.classList.add("select-styled");
        // Pega o texto da opção atualmente selecionada no HTML nativo
        styledSelect.textContent = select.options[select.selectedIndex]?.text || "Selecione...";
        container.appendChild(styledSelect);

        // 3. Cria a lista ul que guardará as novas opções customizadas
        const optionsList = document.createElement("ul");
        optionsList.classList.add("select-options");

        // 4. Varre os elementos filhos do select original para replicar os optgroups e options
        Array.from(select.children).forEach(child => {
            if (child.tagName === "OPTGROUP") {
                // Se for um grupo, cria um item de título na lista
                const groupTitle = document.createElement("li");
                groupTitle.classList.add("select-group-title");
                groupTitle.textContent = child.label;
                optionsList.appendChild(groupTitle);

                // Adiciona as opções de dentro desse grupo
                Array.from(child.children).forEach(option => {
                    createCustomOption(option, optionsList, select, styledSelect, container);
                });
            } else if (child.tagName === "OPTION") {
                // Se for uma opção fora de grupo (caso mude futuramente)
                createCustomOption(child, optionsList, select, styledSelect, container);
            }
        });

        container.appendChild(optionsList);

        // Evento para abrir/fechar o dropdown ao clicar no botão principal
        styledSelect.addEventListener("click", function (e) {
            e.stopPropagation();
            // Fecha outros custom selects abertos antes de abrir este
            document.querySelectorAll(".custom-select-container").forEach(el => {
                if (el !== container) el.classList.remove("active");
            });
            container.classList.toggle("active");
        });
    });

    // Função auxiliar para gerar cada li customizado
    function createCustomOption(option, list, nativeSelect, styledDisplay, container) {
        const li = document.createElement("li");
        li.setAttribute("data-value", option.value);
        li.textContent = option.text;

        li.addEventListener("click", function (e) {
            e.stopPropagation();
            
            // Atualiza o texto do botão visível
            styledDisplay.textContent = option.text;
            
            // Altera o valor no select original oculto
            nativeSelect.value = option.value;
            
            // Fecha o menu
            container.classList.remove("active");

            // CRUCIAL: Dispara o evento de 'change' no select nativo.
            // Isso garante que sua função carregarGrafico() ou submissões JS continuem funcionando!
            nativeSelect.dispatchEvent(new Event("change"));
        });

        list.appendChild(li);
    }

    // Fecha o dropdown caso o usuário clique em qualquer outro lugar da tela
    document.addEventListener("click", function () {
        document.querySelectorAll(".custom-select-container").forEach(container => {
            container.classList.remove("active");
        });
    });
});