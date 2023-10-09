rule get_spreadsheet:
    output:
        vmr="results/vmr.xlsx",
    params:
        link="https://ictv.global/vmr/current",
    shell:
        """
        curl {params.link} > {output.vmr}
        """


rule convert_to_tsv:
    input:
        xlsx="results/vmr.xlsx",
    output:
        tsv="results/vmr.tsv",
    run:
        import pandas as pd

        df = pd.read_excel(input.xlsx, sheet_name=0)
        df.to_csv(output.tsv, sep="\t", index=False)


rule taxonomy_to_tree:
    input:
        tsv="results/vmr.tsv",
    output:
        tree="results/tree.nwk",
    shell:
        """
        python scripts/taxonomy_to_tree.py {input.tsv} {output.tree}
        """


