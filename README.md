# Unsupervised Semantic Abstractive Summarization

This repo contains the source code of acl-srw 2020 work on the AMR (Abstract Meaning Representation) based approach for abstractive summarization i.e. source code of [**Unsupervised Semantic Abstractive Summarization**](https://www.aclweb.org/anthology/P18-3011.pdf) paper. You can find all the details in the following - 

## Datasets - 
* Any summarization dataset
* To get the gold-standard AMR parses you need to get membership on the Linguistic Data Consortium

## Requirements -
* [AMR Parser](https://github.com/RikVN/AMR) - To convert text to its AMR.
* [AMR Generator](https://github.com/sinantie/NeuralAmr) - To convert AMRs to text.
* [AMR library](https://github.com/shibhansh/amr_library) - To obtain AMR for sentences.
* [ROUGE](https://www.aclweb.org/anthology/W04-1013.pdf) - To evaluate the quality.

## Preprocessing - 
* Convert individual sentence to one lined AMR using the [AMR Parser](https://github.com/RikVN/AMR)
* Combine the sentences to get the files in the format similar to the proxy report section of the [AMR bank](https://github.com/shibhansh/amr_library)
* Run to convert to the required format
```sh
$ python generate_amr_file.py --story_file stories.txt --summary_file target_summaries.txt
```

## Summarize -
* Run `python2.7 pipeline.py --input_file path_to_file --dataset name_of_the_dataset` to generate the summary amrs
* `pipeline.py` uses appended [AMR Library](https://github.com/shibhansh/amr_library) to perform all the functions

## Postprocessing - 
* Convert individual generated summary AMRs back to sentences using the [AMR Generator](https://github.com/sinantie/NeuralAmr)
* Put the generated sentences file `predicted_summaries.txt` in `/auxiliary` 
* Combine sentences to produce final summary with `python merge_summary_sentences.py`
* Run [ROUGE](https://www.aclweb.org/anthology/W04-1013.pdf) to evaluate

## Recommended Citation
```sh
@inproceedings{dohare-etal-2018-unsupervised,
    title = "Unsupervised Semantic Abstractive Summarization",
    author = "Dohare, Shibhansh  and
      Gupta, Vivek  and
      Karnick, Harish",
    booktitle = "Proceedings of {ACL} 2018, Student Research Workshop",
    month = jul,
    year = "2018",
    address = "Melbourne, Australia",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/P18-3011",
    doi = "10.18653/v1/P18-3011",
    pages = "74--83",
    abstract = "Automatic abstractive summary generation remains a significant open problem for natural language processing. In this work, we develop a novel pipeline for Semantic Abstractive Summarization (SAS). SAS, as introduced by Liu et. al. (2015) first generates an AMR graph of an input story, through which it extracts a summary graph and finally, creates summary sentences from this summary graph. Compared to earlier approaches, we develop a more comprehensive method to generate the story AMR graph using state-of-the-art co-reference resolution and Meta Nodes. Which we then use in a novel unsupervised algorithm based on how humans summarize a piece of text to extract the summary sub-graph. Our algorithm outperforms the state of the art SAS method by 1.7{\%} F1 score in node prediction.",
}
```

## Main Link
* [ACL-SRW 2018 Paper](https://www.aclweb.org/anthology/P18-3011.pdf)
* [arXiv PrePrint](https://arxiv.org/pdf/1706.01678.pdf)
