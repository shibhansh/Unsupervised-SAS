# Unsupervised Semantic Abstractive Summarization

This repo contains the source code of the AMR (Abstract Meaning Representation) based approach for abstractive summarization. You can find all the details in the following [here] - 

## Datasets - 
* Any summarization dataset
* To get the gold-standard AMR parses you need to get membership on the Linguistic Data Consortium

## Requirements -
* [AMR Parser] - To convert text to its AMR
* [AMR Generator] - To convert AMRs to text
* ROUGE - To evaluate the quality

##Preprocessing - 
* Convert individual sentence to one lined AMR using the [AMR Parser]
* Combine the sentences to get the files in the format similar to the proxy report section of the AMR bank
* Run to convert to the required format
```sh
$ python generate_amr_file.py --story_file stories.txt --summary_file target_summaries.txt
```

##Summarize
* Run `python2.7 pipeline.py --input_file path_to_file --dataset name_of_the_dataset` to generate the summary amrs
* `pipeline.py` uses appended [amr library] to perform all the functions

##Postprocessing - 
* Convert individual generated summary AMRs back to sentences using the [AMR generator]
* Put the generated sentences file `predicted_summaries.txt` in `/auxiliary` 
* Combine sentences to produce final summary `python merge_summary_sentences.py`
* Run ROUGE to evaluate

[AMR Parser]: <https://github.com/RikVN/AMR>
[AMR Generator]: <https://github.com/sinantie/NeuralAmr>
[amr library]: <https://github.com/shibhansh/amr_library>
[here]: <https://arxiv.org/abs/1706.01678>