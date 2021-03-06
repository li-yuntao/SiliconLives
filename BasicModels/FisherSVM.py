# coding: utf-8

import numpy as np
import scipy.io


class MatUtil():
    """
    扩展矩阵运算类
    """

    def __init__(self):
        pass

    @staticmethod
    def mat_dot(mats):
        """
        多矩阵乘法
        :param mats:矩阵列表
        :return: 矩阵乘积
        """
        ret = mats[0]
        for mat in mats[1:]:
            ret = np.dot(ret, mat)
        return ret


class Fisher(object):
    def __init__(self, data, label):
        """
        传入样本，并训练模型
        :param data: 数据样本，n_sample*n_dim
        :param label: 标签n_sample
        """
        self.data = data
        self.label = label
        self.dim = self.data0 = self.data1 = None
        self.w = self.c0 = self.c1 = None
        self.analyse_data()
        self.train()
        self.gc()

    def analyse_data(self):
        self.dim = self.data.shape[1]
        self.data0 = self.data[self.label == 0]
        self.data1 = self.data[self.label == 1]

    def gc(self):
        del self.dim
        del self.data0
        del self.data1

    @staticmethod
    def calc_avg_conv(data):
        mu = np.mean(data, axis=0)  # 1 * n_feature
        conv = np.zeros((data.shape[1], data.shape[1]))  # n_dim * n_dim
        for _sample in data:
            _sample = _sample.reshape((-1, 1)) - mu
            conv += np.dot(_sample, _sample.T)
        return mu, conv

    def train(self):
        self.analyse_data()
        u0, conv0 = self.calc_avg_conv(self.data0)
        u1, conv1 = self.calc_avg_conv(self.data1)
        p0 = self.data0.shape[0] / self.data.shape[0]
        p1 = self.data1.shape[0] / self.data.shape[0]
        s_w = p0 * conv0 + p1 * conv1
        s_b = p0 * p1 * np.dot((u0 - u1), (u0 - u1).T)
        u, sigma, v = np.linalg.svd(s_w)
        inv_s_w = MatUtil.mat_dot([v.T, np.linalg.inv(np.diag(sigma)), u.T])
        self.w = np.dot(inv_s_w, u0 - u1)
        self.c0 = np.dot(self.w.T, u0)
        self.c1 = np.dot(self.w.T, u1)

    def predict(self, sample):
        sample = np.array(sample)
        project = np.dot(self.w.T, sample.T)
        d0 = abs(project - self.c0)
        d1 = abs(project - self.c1)
        return 0 if d0 < d1 else 1


if __name__ == '__main__':
    sample_label_data = scipy.io.loadmat('data.mat')['data']
    sample_data = sample_label_data[:, :-1]
    label_data = sample_label_data[:, -1]
    fisher = Fisher(sample_data, label_data)
    correct, cnt = 0, 0
    for sample, label in zip(sample_data, label_data):
        ret = fisher.predict(sample.reshape(1, -1))
        if ret == label:
            correct += 1
        cnt += 1
    print('fisher acc = %.4f' % (correct / cnt))
