library(ggplot2)
library(reshape2)

xls = c(5.18,6.15,7.33,6.38,7.39,6.75,5.6,6.79,2.61,2.85,6.15,9.33,4.45,4.82,3.72,7.05,7.47,5.47)
py = c(5.41,5.99,6.82,7.76,6.9,8.95,4.89,6.15,2.1,2.33,7.51,9.08,4.22,4.48,2.89,6.11,6.18,5.52)
#py = c(5.41,5.99,6.82,7.76,6.9,9.05,4.89,6.15,2.1,2.33,7.51,9.08,4.22,4.97,2.89,6.11,6.18,5.52)
group = as.factor(c('Tc','Ho','Tc','Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho','Tc', 'Ho'))
patient_id = as.factor(c(1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9))
study_id = as.factor(1:18)
df = data.frame(study_id, patient_id, group, xls, py)


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

ggplot(data = melt(df), aes(x=study_id, y=value, color=variable)) +
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

ggplot(data = melt(df), aes(x=patient_id, y=value, color=group, shape=variable)) +
  geom_point() +
  geom_hline(yintercept=2.69, linetype="dashed", color="black", size=.5) +
  theme(plot.title = element_text(hjust = 0.5), legend.title = element_blank()) +
  scale_shape(labels = c("ISP + xls", "Python")) +
  scale_color_hue(labels = c("Post Ho166-PLLA", "Tc99m-IDA")) +
  labs(title='Overview of results compared to clinical cutoff', y="Liver clearance", x='patient id')
