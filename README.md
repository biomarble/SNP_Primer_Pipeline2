# KASP/Caps Primer pipeline
a modified version of [SNP_Primer_Pipeline2](https://github.com/pinbo/SNP_Primer_Pipeline2)


## KASP引物设计

![KASP标记](http://www.cgmb.com.cn/culture/Public/Home/images/20161108/1478594766762578.jpg)

```bash
mamba create -n primer primer3 bedtools vcftools seqkit muscle  blast
conda activate primer 
```

### 给参考基因组建立 blast数据库
```bash
makeblastdb -in data/sequences.fa -dbtype nucl -parse_seqids 
```

### 输入文件预处理


位置文件预处理，获取SNP附近的序列

```bash
nohup SNP_Primer_Pipeline/SNP_PosInfo.py  data/snp.pos.txt  data/sequences.fa  pos.info.csv  100 >PrepareRun.log
```
|参数|含义|
|-|-|
|data/snp.pos.txt|输入位置文件；<br>Tab分隔的文本格式,无表头<br>文件共四列：染色体编号，位置，REF Alle， ALT Alle|
|data/sequences.fa|已建立好blast数据库的基因组序列|
|pos.info.csv|输出文件|
|100|SNP侧翼序列范围|

### 引物设计

运行流程，获取KASP与CAPS引物

```bash
mkdir KASP_design_output #新建输出结果目录
cd KASP_design_output  #进入输出结果目录

nohup ../SNP_Primer_Pipeline/run_getkasp.py  ../pos.info.csv    200    0    1   63    25   ../data/sequences.fa   >PickPrimer.log
```

|参数|含义|
|-|-|
| ../pos.info.csv|  SNP_PosInfo.py得到的位置文件，其中包括了flanking sequence,|
| 200| 候选酶的最高价格 ( 美元/1000 U) |
| 0| 是否设计CAPS引物 (1 for yes and 0 for NO)|
| 1| 是否设计KASP引物 (1 for yes and 0 for NO)|
| 63| 最大退火温度 Tm |
| 25| 引物最大长度|
| ../data/sequences.fa | 参考序列位置（需事先建立好blast数据库）|

>KSAP引物设计程序核心为张军利博士的SNP_Primer_Pipeline2(https://github.com/pinbo/SNP_Primer_Pipeline2) ，仅做易用性优化

