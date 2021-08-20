#https://www.statskingdom.com/320ShapiroWilk.html
library(ggplot2)
library(ggcorrplot)
library(reshape2)

xls = c(5.18,6.15,7.33,6.38,7.39,6.75,5.6,6.79,2.61,2.85,6.15,9.33,4.45,4.82,3.72,7.05,7.47,5.47,4.91,4.86,4.22,3.49,3.82,5.52,4.45,3.83)
py = c(5.66,6.23,7.79,8.59,7.25,9.27,5.35,6.59,2.35,2.39,7.83,9.27,4.33,4.61,3.16,6.51,7.04,5.67,4.94,4.98,4.41,4.02,4.71,5.33,4.07,4.17) #oli
pyInfi = c(5.79,6.62,7.27,9.04,7.82,9.70,5.19,6.92,2.33,2.40,8.48,9.43,4.06,5.15,2.65,6.26,7.53,5.70,5.09,4.55,4.24,3.39,3.95,4.93,3.73,3.71) #infi

group = as.factor(c('Tc','Ho','Tc','Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho'))
patient_id = as.factor(c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13))
study_id = as.factor(1:26)
age =    c(74,74,87,87,61,61,78,78,51,51,50,50,75,75,64,64,94,94,58,58,58,58,80,80,58,58)
weight = c(64,65,71,71,73,73,92.5,92.5,85,85,66,68,86,86,71,71,73,73,98.6,98.6,98.6,98.6,99,99,96,96)
size =   c(164,164,170,170,171,171,168,168,183,183,172,172,174,174,165,165,176,176,176,176,176,176,172,172,176,176)
inr =    c(1.01,1.01,1.08,1.08,1.08,1.08,1.02,1.02,1.17,1.17,1.09,1.09,1.01,1.01,1.26,1.26,1.06,1.06,1.00,1.00,1.02,1.02,1.04,1.04,1.04,1.04)
bili =   c(1.20,1.20,0.64,0.64,0.88,0.88,0.22,0.22,1.20,1.20,0.21,0.21,0.50,0.50,0.96,0.96,0.38,0.38,0.50,0.50,0.94,0.94,1.00,1.00,0.88,0.88)
albu =   c(41,41,48,48,47,47,41,41,34,34,41,41,46,46,28,28,39,39,46,46,45,45,41,41,43,43)
albi = log10(bili)*0.66+albu*(-0.085)
df = data.frame(study_id, patient_id, group, xls, py, pyInfi, age, weight, size, inr, bili, albu, albi)


# ============================== xls vs. py ==============================

#sans les données des patient 11 et 13 pour les t-test (meme personne que patient 10)
xls_ = c(5.18,6.15,7.33,6.38,7.39,6.75,5.6,6.79,2.61,2.85,6.15,9.33,4.45,4.82,3.72,7.05,7.47,5.47,4.91,4.86,3.82,5.52)
py_ = c(5.66,6.23,7.79,8.59,7.25,9.27,5.35,6.59,2.35,2.39,7.83,9.27,4.33,4.61,3.16,6.51,7.04,5.67,4.94,4.98,4.71,5.33)
pyInfi_ = c(5.79,6.62,7.27,9.04,7.82,9.70,5.19,6.92,2.33,2.40,8.48,9.43,4.06,5.15,2.65,6.26,7.53,5.70,5.09,4.55,3.95,4.93)
group_ = as.factor(c('Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho'))
patient_id_ = as.factor(c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,12,12))
df_ = data.frame(patient_id_, group_, xls_, py_, pyInfi_)

ggplot(data = melt(df[c('xls', 'pyInfi')]), aes(x=variable, y=value)) +
  geom_violin(trim=FALSE) +
  geom_boxplot(width=0.1) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("ISP + xls","HBS_Tools (Infi)"))+
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=0.8) +
  labs(title="Manual vs. automated approach", y=("Liver clearance"), x=(''))

test_xls = round(shapiro.test(xls_)$p.value,3) # >0.05 distrib normale à confirmer
test_py = round(shapiro.test(pyInfi_)$p.value,3)# >0.05 distrib normale à confirmer
t.test(xls_, pyInfi_, paired=TRUE)# >alpha, la différence entre les moyennes n'est pas significative

ggplot(data = melt(df_short), aes(x=study_id, y=value, color=variable)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color = "black") +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_color_hue(labels = c("ISP+xls", "Python")) +
  labs(title='ISP+xls and py compared to clinical cutoff', y="Liver clearance", x='study id')


# ============================== pre-Ho vs. post-Ho py ==============================


ggplot(df_, aes(x=group_, y=py_, group=group_)) +
  geom_violin(trim=FALSE) +
  geom_boxplot(width=0.1) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("Post Ho166-PLLA","Tc99m-IDA")) +
  labs(title="Tc99m-IDA vs. Post Ho166-PLLA with automated approach", y="Liver clearance (nurse processing)", x='')

test = round(shapiro.test(df_[df_$group_=='Tc','pyInfi_'])$p.value,3)# >0.05 distrib normale à confirmer
test = round(shapiro.test(df_[df_$group_=='Ho','pyInfi_'])$p.value,3)# >0.05 distrib normale à confirmer
t.test(df_[df_$group_=='Tc','pyInfi_'], df_[df_$group_=='Ho','pyInfi_'], paired=TRUE)# <0.05 différence entre les moyennes est statistiquement significative

ggplot(data = df, aes(x=patient_id, y=py, color=group)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color = "black") +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Tc99m-IDA")) +
  labs(title='Python results compared to clinical cutoff', y="Liver clearance", x='patient id')


# ============================== pre-Ho vs. post-Ho ISP+xls ==============================


ggplot(df_, aes(x=group_, y=xls_, group=group_)) +
  geom_violin(trim=FALSE) +
  geom_boxplot(width=0.1) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("Post Ho166-PLLA","Tc99m-IDA")) +
  labs(title="Tc99m-IDA vs. Post Ho166-PLLA with manual approach", y="Liver clearance", x='')

test = round(shapiro.test(df_[df_$group_=='Tc','xls_'])$p.value,3)# >0.05 distrib normale à confirmer
test = round(shapiro.test(df_[df_$group_=='Ho','xls_'])$p.value,3)# >0.05 distrib normale à confirmer
t.test(df_[df_$group_=='Tc','xls_'], df_[df_$group_=='Ho','xls_'], paired=TRUE)# >0.05

ggplot(data = df, aes(x=patient_id, y=xls, color=group)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color = "black") +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Tc99m-IDA")) +
  labs(title='ISP+xls results compared to clinical cutoff', y="Liver clearance", x='patient id')


# ============================== Overview ==============================

df_short = data.frame(study_id, patient_id, group, xls, pyInfi)
ggplot(data = melt(df_short), aes(x=patient_id, y=value, color=group, shape=variable)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color="black", size=.5) +
  theme(plot.title = element_text(hjust = 0.5), legend.title = element_blank()) +
  scale_shape(labels = c("ISP + xls", "HBS_Tools")) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Pré Ho166-PLLA")) +
  labs(title='Overview of results compared to clinical cutoff', y="Liver clearance (nurse processing)", x='patient id')


# ======================== Clinical data py vs xls =========================


#df_num = data.frame(xls, pyInfi, inr, bili, albu, albi)
df_num = data.frame(xls, pyInfi, inr, bili, albu, albi)
names(df_num)[names(df_num) == "xls"] <- "ISP + xls"
names(df_num)[names(df_num) == "py"] <- "HBS_Tools"
names(df_num)[names(df_num) == "bili"] <- "bilirubine"
names(df_num)[names(df_num) == "albu"] <- "albumine"
names(df_num)[names(df_num) == "albi"] <- "albi score"
names(df_num)[names(df_num) == "pyInfi"] <- "HBS_Tools"
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix", y='', x='')

plot(df$py, df$inr, col='red', pch=1, xlab='liver clearance', ylab='inr')
points(df$xls, df$inr, col='blue', pch=2)
abline(lm(df$inr ~ df$py), col='red')
abline(lm(df$inr ~ df$xls), col='blue')
legend("topright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)
cor.test(df$inr, df$py)
cor.test(df$inr, df$xls)

plot(df$py, df$bili, col='red', pch=1, xlab='liver clearance', ylab='bilirubine')
points(df$xls, df$bili, col='blue', pch=2)
abline(lm(df$bili ~ df$py), col='red')
abline(lm(df$bili ~ df$xls), col='blue')
legend("topright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)
cor.test(df$bili, df$py)
cor.test(df$bili, df$xls)

plot(df$py, df$albu, col='red', pch=1, xlab='liver clearance', ylab='albumine')
points(df$xls, df$albu, col='blue', pch=2)
abline(lm(df$albu ~ df$py), col='red')
abline(lm(df$albu ~ df$xls), col='blue')
legend("bottomright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)
cor.test(df$albu, df$py)
cor.test(df$albu, df$pyInfi)
cor.test(df$albu, df$xls)

plot(df$py, df$albi, col='red', pch=1, xlab='liver clearance', ylab='albi score')
points(df$xls, df$albi, col='blue', pch=2)
abline(lm(df$albi ~ df$py), col='red')
abline(lm(df$albi ~ df$xls), col='blue')
legend("topright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)
cor.test(df$albi, df$py)
cor.test(df$albi, df$pyInfi)
cor.test(df$albi, df$xls)


# ======================== Clinical data pre-Ho vs. post-Ho =========================


df_num = df[df$group=='Tc',c('xls', 'pyInfi', 'inr', 'bili', 'albu', 'albi')]
names(df_num)[names(df_num) == "pyInfi"] <- "HBS_Tools"
names(df_num)[names(df_num) == "xls"] <- "ISP + xls"
names(df_num)[names(df_num) == "bili"] <- "bilirubine"
names(df_num)[names(df_num) == "albu"] <- "albumine"
names(df_num)[names(df_num) == "albi"] <- "albi score"
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix (Tc99 data)", y='', x='')

df_num = df[df$group=='Ho',c('xls', 'pyInfi', 'inr', 'bili', 'albu', 'albi')]
names(df_num)[names(df_num) == "pyInfi"] <- "HBS_Tools I"
names(df_num)[names(df_num) == "xls"] <- "ISP + xls"
names(df_num)[names(df_num) == "bili"] <- "bilirubine"
names(df_num)[names(df_num) == "albu"] <- "albumine"
names(df_num)[names(df_num) == "albi"] <- "albi score"
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix (Post Ho166-PLLA data)", y='', x='')

#===

plot(df[df$group=='Tc','py'], df[df$group=='Tc','inr'], col='red', pch=1, xlab='liver clearance', ylab='inr')
points(df[df$group=='Ho','py'], df[df$group=='Ho','inr'], col='blue', pch=2)
legend("bottomleft", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. inr (python data)")

plot(df[df$group=='Tc','xls'], df[df$group=='Tc','inr'], col='red', pch=1, xlab='liver clearance', ylab='inr')
points(df[df$group=='Ho','xls'], df[df$group=='Ho','inr'], col='blue', pch=2)
legend("bottomleft", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. inr (ISP+xls data)")

#===

plot(df[df$group=='Tc','py'], df[df$group=='Tc','bili'], col='red', pch=1, xlab='liver clearance', ylab='bili')
points(df[df$group=='Ho','py'], df[df$group=='Ho','bili'], col='blue', pch=2)
legend("topright", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. bilirubine (python data)")

plot(df[df$group=='Tc','xls'], df[df$group=='Tc','bili'], col='red', pch=1, xlab='liver clearance', ylab='bili')
points(df[df$group=='Ho','xls'], df[df$group=='Ho','bili'], col='blue', pch=2)
legend("topright", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. bilirubine (ISP+xls data)")

#===

plot(df[df$group=='Tc','py'], df[df$group=='Tc','albu'], col='red', pch=1, xlab='liver clearance', ylab='albu')
points(df[df$group=='Ho','py'], df[df$group=='Ho','albu'], col='blue', pch=2)
legend("topleft", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. albumine (python data)")

plot(df[df$group=='Tc','xls'], df[df$group=='Tc','albu'], col='red', pch=1, xlab='liver clearance', ylab='albu')
points(df[df$group=='Ho','xls'], df[df$group=='Ho','albu'], col='blue', pch=2)
legend("topleft", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. albumine (ISP+xls data)")

#===

plot(df[df$group=='Tc','py'], df[df$group=='Tc','albi'], col='red', pch=1, xlab='liver clearance', ylab='albi score')
points(df[df$group=='Ho','py'], df[df$group=='Ho','albi'], col='blue', pch=2)
legend("bottomleft", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. albi score (python data)")

plot(df[df$group=='Tc','xls'], df[df$group=='Tc','albi'], col='red', pch=1, xlab='liver clearance', ylab='albi score')
points(df[df$group=='Ho','xls'], df[df$group=='Ho','albi'], col='blue', pch=2)
legend("bottomleft", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
title("Liver clearance vs. albi score (ISP+xls data)")


# ======================== Ho interference correction =========================


corr = c(6.23,8.59,9.27,6.59,2.39,9.27,4.61,6.51,5.67,4.98,4.02,5.33,4.17)
nc = c(5.72,6.44,8.98,6.46,2.3,7.8,3.85,5.06,4.65,4.16,3.3,4.68,3.87)
corr_ = c(6.23,8.59,9.27,6.59,2.39,9.27,4.61,6.51,5.67,4.98,5.33)
nc_ = c(5.72,6.44,8.98,6.46,2.3,7.8,3.85,5.06,4.65,4.16,4.68)
lab = as.factor(c("corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","raw","raw","raw","raw","raw","raw","raw","raw","raw","raw","raw","raw","raw"))
lab_ = as.factor(c("corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","corrected","raw","raw","raw","raw","raw","raw","raw","raw","raw","raw","raw"))
val = c(corr_, nc_)
df= data.frame(val, lab_)

test = round(shapiro.test(corr_)$p.value,3)# >0.05 distrib normale à confirmer
test = round(shapiro.test(nc_)$p.value,3)# >0.05 distrib normale à confirmer
t.test(corr_, nc_, paired=TRUE)

ggplot(df, aes(x=lab_, y=val)) +
  geom_violin(trim=FALSE) +
  geom_boxplot(width=0.1) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("Corrected","Raw")) +
  labs(title="Corrected vs. raw  (automated approach)", y="Liver clearance", x='')

df_num = df[df$group=='Ho',c('inr', 'bili', 'albu', 'albi')]
df_num$corrected = corr
df_num$raw = nc
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix (Post Ho166-PLLA data)", y='', x='')
