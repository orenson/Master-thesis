library(ggplot2)
library(ggcorrplot)
library(reshape2)

xls = c(5.18,6.15,7.33,6.38,7.39,6.75,5.6,6.79,2.61,2.85,6.15,9.33,4.45,4.82,3.72,7.05,7.47,5.47,4.91,4.86)
py = c(5.41,5.99,6.82,7.76,6.9,8.95,4.89,6.15,2.1,2.33,7.51,9.08,4.22,4.48,3.07,6.25,6.18,5.52,4.88,4.73)
#py = c(5.41,5.99,6.82,7.76,6.9,9.05,4.89,6.15,2.1,2.33,7.51,9.08,4.22,4.97,2.89,6.11,6.18,5.52,XXX,XXX)
group = as.factor(c('Tc','Ho','Tc','Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho'))
patient_id = as.factor(c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10))
study_id = as.factor(1:20)
age = c(74,74,87,87,61,61,78,78,51,51,50,50,75,75,64,64,94,94,58,58)
weight = c(64,65,71,71,73,73,92.5,92.5,85,85,66,68,86,86,70.8,70.8,73,73,98.6,98.6)
size = c(164,164,170,170,171,171,168,168,183,183,172,172,174,174,165,165,176,176,176,176)
inr = c(1.01,1.01,1.08,1.08,1.08,1.08,1.02,1.02,1.17,1.17,1.09,1.09,1.01,1.01,NaN,NaN,1.06,1.06,NaN,NaN)
bili = c(1.2,1.2,0.64,0.64,0.88,0.88,0.22,0.22,1.2,1.2,0.21,0.21,0.5,0.5,NaN,NaN,0.38,0.38,NaN,NaN)
albu = c(41,41,48,48,47,47,41,41,34,34,41,41,46,46,NaN,NaN,39,39,NaN,NaN)
df = data.frame(study_id, patient_id, group, xls, py, age, weight, size, inr, bili, albu)
df_short = data.frame(study_id, patient_id, group, xls, py)
df_num = data.frame(xls, py, age, weight, size, inr, bili, albu)


# ============================== xls vs. py ==============================

boxplot(df[,c('xls','py')], notch=TRUE)
title('Manual vs. automated approach')
#recouvrement +++ xls et py sont idem
ggplot(data = melt(df[c('xls','py')]), aes(x=variable, y=value)) + 
  geom_violin(trim=FALSE) + 
  geom_boxplot(width=0.1) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_x_discrete(labels=c("ISP + xls","py"))+
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
  labs(title="Tc99m-IDA vs. Post Ho166-PLLA with automated approach", y="Liver clearance", x='')

test = round(shapiro.test(df[df$group=='Tc','py'])$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[df$group=='Tc','py']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("Tc99m-IDA histogram (p-val =", toString(test), ")") , y="density", x='Liver clearance')

test = round(shapiro.test(df[df$group=='Ho','py'])$p.value,3)# >0.05 distrib normale à confirmer
ggplot(data = melt(df[df$group=='Ho','py']), aes(x=value)) +
  geom_histogram(aes(y=..density..), bins=10, color="black", fill="white") +
  geom_density(alpha=0.2, fill="#FF6666") +
  theme(plot.title = element_text(hjust = 0.5)) +
  labs(title=paste("Post Ho166-PLLA histogram (p-val =", toString(test), ")") , y="density", x='Liver clearance')

t.test(df[df$group=='Tc','py'], df[df$group=='Ho','py'], paired=TRUE)# <0.05 différence entre les moyennes est statistiquement significative

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

ggplot(data = melt(df_short), aes(x=patient_id, y=value, color=group, shape=variable)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color="black", size=.5) +
  theme(plot.title = element_text(hjust = 0.5), legend.title = element_blank()) +
  scale_shape(labels = c("ISP + xls", "Python")) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Tc99m-IDA")) +
  labs(title='Overview of results compared to clinical cutoff', y="Liver clearance", x='patient id')



# ======================== Clinical variables py vs xls =========================

mat <- round(cor(df_num, use = "complete.obs", method = "pearson"),2)
ggcorrplot(mat, type = "lower", p.mat = cor_pmat(df_num, use = "complete.obs", method = "pearson"))

plot(df$py, df$inr, col='red', pch=1, xlab='liver clearance', ylab='inr')
points(df$xls, df$inr, col='blue', pch=2)
abline(lm(df$inr ~ df$py), col='red')
abline(lm(df$inr ~ df$xls), col='blue')
legend("topright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)

plot(df$py, df$bili, col='red', pch=1, xlab='liver clearance', ylab='bilirubine')
points(df$xls, df$bili, col='blue', pch=2)
abline(lm(df$bili ~ df$py), col='red')
abline(lm(df$bili ~ df$xls), col='blue')
legend("topright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)

plot(df$py, df$albu, col='red', pch=1, xlab='liver clearance', ylab='albumine')
points(df$xls, df$albu, col='blue', pch=2)
abline(lm(df$albu ~ df$py), col='red')
abline(lm(df$albu ~ df$xls), col='blue')
legend("bottomright", legend=c("python", "ISP + xls"), col=c("red", "blue"), pch=1:2)

# ======================== Clinical variables Tc vs Ho =========================

plot(df[df$group=='Tc','py'], df[df$group=='Tc','inr'], col='red', pch=1, xlab='liver clearance', ylab='inr')
points(df[df$group=='Tc','xls'], df[df$group=='Tc','inr'], col='red', pch=1)
points(df[df$group=='Ho','py'], df[df$group=='Ho','inr'], col='blue', pch=2)
points(df[df$group=='Ho','xls'], df[df$group=='Ho','inr'], col='blue', pch=2)
#abline(lm(df$inr ~ df$py), col='red')
#abline(lm(df$inr ~ df$xls), col='blue')
legend("topright", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)

plot(df[df$group=='Tc','py'], df[df$group=='Tc','bili'], col='red', pch=1, xlab='liver clearance', ylab='bili')
points(df[df$group=='Tc','xls'], df[df$group=='Tc','bili'], col='red', pch=1)
points(df[df$group=='Ho','py'], df[df$group=='Ho','bili'], col='blue', pch=2)
points(df[df$group=='Ho','xls'], df[df$group=='Ho','bili'], col='blue', pch=2)
#abline(lm(df$inr ~ df$py), col='red')
#abline(lm(df$inr ~ df$xls), col='blue')
legend("topright", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)

plot(df[df$group=='Tc','py'], df[df$group=='Tc','albu'], col='red', pch=1, xlab='liver clearance', ylab='albu')
points(df[df$group=='Tc','xls'], df[df$group=='Tc','albu'], col='red', pch=1)
points(df[df$group=='Ho','py'], df[df$group=='Ho','albu'], col='blue', pch=2)
points(df[df$group=='Ho','xls'], df[df$group=='Ho','albu'], col='blue', pch=2)
#abline(lm(df$inr ~ df$py), col='red')
#abline(lm(df$inr ~ df$xls), col='blue')
legend("bottomright", legend=c("Tc", "Ho"), col=c("red", "blue"), pch=1:2)
