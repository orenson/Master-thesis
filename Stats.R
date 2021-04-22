#https://www.statskingdom.com/320ShapiroWilk.html
library(ggplot2)
library(ggcorrplot)
library(reshape2)

xls = c(5.18,6.15,7.33,6.38,7.39,6.75,5.6,6.79,2.61,2.85,6.15,9.33,4.45,4.82,3.72,7.05,7.47,5.47,4.91,4.86)
py = c(5.66,6.23,7.79,8.59,7.25,9.27,5.35,6.59,2.35,2.39,7.83,9.27,4.33,4.61,3.16,6.51,7.04,5.67,4.94,4.98) #oli
pyInfi = c(5.79,6.62,7.27,9.04,7.82,9.70,5.19,6.92,2.33,2.40,8.48,9.43,4.06,5.15,2.65,6.26,7.53,5.70,5.09,4.55) #infi

group = as.factor(c('Tc','Ho','Tc','Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho'))
patient_id = as.factor(c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10))
study_id = as.factor(1:20)
age =    c(74,74,87,87,61,61,78,78,51,51,50,50,75,75,64,64,94,94,58,58)
weight = c(64,65,71,71,73,73,92.5,92.5,85,85,66,68,86,86,71,71,73,73,98.6,98.6)
size =   c(164,164,170,170,171,171,168,168,183,183,172,172,174,174,165,165,176,176,176,176)
inr =    c(1.01,1.01,1.08,1.08,1.08,1.08,1.02,1.02,1.17,1.17,1.09,1.09,1.01,1.01,1.26,1.26,1.06,1.06,1.00,1.00)
bili =   c(1.20,1.20,0.64,0.64,0.88,0.88,0.22,0.22,1.20,1.20,0.21,0.21,0.50,0.50,0.96,0.96,0.38,0.38,0.50,0.50)
albu =   c(41,41,48,48,47,47,41,41,34,34,41,41,46,46,28,28,39,39,46,46)
albi = log10(bili)*0.66+albu*(-0.085)
df = data.frame(study_id, patient_id, group, xls, py, pyInfi, age, weight, size, inr, bili, albu, albi)


# ============================== xls vs. py ==============================


boxplot(df[,c('xls','py')], notch=TRUE)
title('Manual vs. automated approach')
#recouvrement +++ xls et py sont idem
ggplot(data = melt(df[c('xls','py', 'pyInfi')]), aes(x=variable, y=value)) + 
  geom_violin(trim=FALSE) + 
  geom_boxplot(width=0.1) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("ISP + xls","Oli","Infi"))+
  labs(title="Manual vs. automated approach", y=("Liver clearance"), x=(''))

test_xls = round(shapiro.test(xls)$p.value,3) # >0.05 distrib normale à confirmer
ggplot(data = melt(df[,'xls']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("ISP+xls histogram (p-val = ", toString(test_xls), ")") , y="density", x='Liver clearance')

test_py = round(shapiro.test(py)$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[,'py']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("py histogram (p-val = ", toString(test_py), ")") , y="density", x='Liver clearance')

t.test(xls, py, paired=TRUE)# >alpha, la différence entre les moyennes n'est pas significative

ggplot(data = melt(df_short), aes(x=study_id, y=value, color=variable)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color = "black") +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_color_hue(labels = c("ISP+xls", "Python")) +
  labs(title='ISP+xls and py compared to clinical cutoff', y="Liver clearance", x='study id')


# ============================== bis py ==============================


boxplot(df$py ~ df$group, notch=TRUE)
title('Tc99m-IDA vs. Post Ho166-PLLA with automated approach')
#recouvrement moin important, box Ho semble plus haute
ggplot(df, aes(x=group, y=py, group=group)) + 
  geom_violin(trim=FALSE) + 
  geom_boxplot(width=0.1) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("Post Ho166-PLLA","Tc99m-IDA")) +
  labs(title="Tc99m-IDA vs. Post Ho166-PLLA with automated approach", y="Liver clearance (xxx processing)", x='')

test = round(shapiro.test(df[df$group=='Tc','pyInfi'])$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[df$group=='Tc','py']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("Tc99m-IDA histogram (p-val =", toString(test), ")") , y="density", x='Liver clearance')

test = round(shapiro.test(df[df$group=='Ho','pyInfi'])$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[df$group=='Ho','py']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("Post Ho166-PLLA histogram (p-val =", toString(test), ")") , y="density", x='Liver clearance')

t.test(df[df$group=='Tc','pyInfi'], df[df$group=='Ho','pyInfi'], paired=TRUE)# <0.05 différence entre les moyennes est statistiquement significative

plot(df[df$group=='Tc','py'], df[df$group=='Ho','py'])
ggplot(data = df, aes(x=patient_id, y=py, color=group)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color = "black") +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Tc99m-IDA")) +
  labs(title='Python results compared to clinical cutoff', y="Liver clearance", x='patient id')


# ============================== bis ISP+xls ==============================


boxplot(df$xls ~ df$group, notch=TRUE)
title('Tc99m-IDA vs. Post Ho166-PLLA with manual approach')
#recouvrement moin important, box Ho semble plus haute
ggplot(df, aes(x=group, y=xls, group=group)) + 
  geom_violin(trim=FALSE) + 
  geom_boxplot(width=0.1) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("Post Ho166-PLLA","Tc99m-IDA")) +
  labs(title="Tc99m-IDA vs. Post Ho166-PLLA with manual approach", y="Liver clearance", x='')

test = round(shapiro.test(df[df$group=='Tc','xls'])$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[df$group=='Tc','xls']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("Tc99m-IDA histogram (p-val =", toString(test), ")") , y="density", x='Liver clearance')

test = round(shapiro.test(df[df$group=='Ho','xls'])$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[df$group=='Ho','xls']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("Post Ho166-PLLA histogram (p-val =", toString(test), ")") , y="density", x='Liver clearance')

t.test(df[df$group=='Tc','xls'], df[df$group=='Ho','xls'], paired=TRUE)# >0.05 

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
  scale_shape(labels = c("ISP + xls", "Python")) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Tc99m-IDA")) +
  labs(title='Overview of results compared to clinical cutoff', y="Liver clearance (nurse processing)", x='patient id')


# ======================== Clinical variables py vs xls =========================


df_num = data.frame(xls, pyInfi, age, weight, size, inr, bili, albu, albi)
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix (Infirmières)", y='', x='')

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


# ======================== Clinical variables Tc vs Ho =========================


df_num = df[df$group=='Tc',c('xls', 'py', 'pyInfi', 'age', 'weight', 'size', 'inr', 'bili', 'albu', 'albi')]
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix (Tc99 data)", y='', x='')

df_num = df[df$group=='Ho',c('xls', 'py', 'pyInfi', 'age', 'weight', 'size', 'inr', 'bili', 'albu', 'albi')]
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


# ======================== pre-processin correction =========================


corr = c(6.23,8.59,9.27,6.59,2.39,9.27,4.61,6.51,5.67,4.98)
nc = c(5.72,6.44,8.98,6.46,2.3,7.8,3.85,5.06,4.65,4.16)
lab = as.factor(c("corr","corr","corr","corr","corr","corr","corr","corr","corr","corr","nc","nc","nc","nc","nc","nc","nc","nc","nc","nc"))
val = c(corr, nc)
df= data.frame(val, lab)

test = round(shapiro.test(corr)$p.value,3)# >0.05 distrib normale à confirmer
test = round(shapiro.test(nc)$p.value,3)# >0.05 distrib normale à confirmer
t.test(corr, nc, paired=TRUE)

ggplot(df, aes(x=lab, y=val)) + 
  geom_violin(trim=FALSE) + 
  geom_boxplot(width=0.1) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("Pre-processed","Raw")) +
  labs(title="Pre-processed vs. raw  (automated approach)", y="Liver clearance", x='')

df_num = df[df$group=='Ho',c('age', 'weight', 'size', 'inr', 'bili', 'albu', 'albi')]
df_num$corr = corr
df_num$nc = nc
mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson")) +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title="Correlation matrix (Post Ho166-PLLA data)", y='', x='')
