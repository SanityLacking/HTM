import numpy as np
import math
import random
import matplotlib.pyplot as plt

DEFAULT_RADIUS = 0
DEFAULT_RESOLUTION = 0

class ScalarEncoder:
    def __init__(self, min_val=0, max_val=20, log_max=1000, delta_min=-10, delta_max=10, out_size=16, w=3 name=""):
        
        self.min_val = min_val                  # 표현할 최소값
        self.max_val = max_val                  # 표현할 최대값
        self.log_max = log_max               # 로그 encoder 최대값
        self.delta_min = delta_min           # delta 최소값
        self.delta_max = delta_max           # delta 최대값
        self.out_size = out_size             # Output Data Size
        self.n = self.out_size
        self.w = w                           # 1 Number of In Bits
        self.halfwidth =  (w - 1) // 2
        self.num_bucket = out_size - w + 1   # bucket 의 갯수
        self.verbosity = 0
        self.periodic = False
        self.resolution = 5  #this needs to change
        self.padding = self.halfwidth
        self.name =""
        self.nInternal
        self.rangeInternal

        #initialize the variables
        self._initEncoder(w, min_val, max_val, self.n, radius, self.resolution)

        # nInternal represents the output area excluding the possible padding on each
        #  side
        if (min_val is not None and max_val is not None):
            self.nInternal = self.n - 2 * self.padding

        # Our name
        if name is not None:
            self.name = name
        else:
            self.name = "[%s:%s]" % (self.min_val, self.max_val)

    def _initEncoder(self, w, min_val, max_val, n, radius, resolution):
        """ (helper function)  There are three different ways of thinking about the representation.
        Handle each case here."""
        if n != 0:
            if (radius !=0 or resolution != 0):
                raise ValueError("Only one of n/radius/resolution can be specified for a ScalarEncoder")
            assert n > w
            self.n = n

        if (min_val is not None and max_val is not None):
            if not self.periodic:
                self.resolution = float(self.rangeInternal) / (self.n - self.w)
            else:
                self.resolution = float(self.rangeInternal) / (self.n)

            self.radius = self.w * self.resolution

            if self.periodic:
                self.range = self.rangeInternal
            else:
                self.range = self.rangeInternal + self.resolution

        else:
            if radius != 0:
                if (resolution != 0):
                    raise ValueError("Only one of radius/resolution can be specified for a ScalarEncoder")
                self.radius = radius
                self.resolution = float(self.radius) / w
            elif resolution != 0:
                self.resolution = float(resolution)
                self.radius = self.resolution * self.w
            else:
                raise Exception("One of n, radius, resolution must be specified for a ScalarEncoder")

            if (min_val is not None and max_val is not None):
                if self.periodic:
                    self.range = self.rangeInternal
                else:
                    self.range = self.rangeInternal + self.resolution

                nfloat = self.w * (self.range / self.radius) + 2 * self.padding
                self.n = int(math.ceil(nfloat))



    def _getFirstOnBit(self, value):
        """ Return the bit offset of the first bit to be set in the encoder output.
        For periodic encoders, this can be a negative number when the encoded output
        wraps around. """
        print(value)
        if value == None:
            return [None]
        
        else:
            if value < self.min_val:
            # Don't clip periodic values. Out-of-range value is always an error
                if self.clipvalue and not self.periodic:
                    if self.verbosity > 0:
                        print("Clipped value %s=%.2f to min_val %.2f" % (self.name, value,self.min_val))
                    value = self.min_val
                else:
                    raise Exception('value (%s) less than range (%s - %s)' %(str(value), str(self.min_val), str(self.max_val)))

        if self.periodic:
        # Don't clip periodic values. Out-of-range value is always an error
            if value >= self.max_val:
                raise Exception('value (%s) greater than periodic range (%s - %s)' %(str(value), str(self.min_val), str(self.max_val)))
        else:
            if value > self.max_val:
                if self.clipvalue:
                    if self.verbosity > 0:
                        print("Clipped value %s=%.2f to max_val %.2f" % (self.name, value,self.max_val))
                    value = self.max_val
                else:
                    raise Exception('value (%s) greater than range (%s - %s)' %(str(value), str(self.min_val), str(self.max_val)))

        if self.periodic:
            centerbin = int((value - self.min_val) * self.nInternal / self.range) + self.padding
        else:
            centerbin = int(((value - self.min_val) + self.resolution/2)  / self.resolution ) + self.padding
                            
        # We use the first bit to be set in the encoded output as the bucket index
        minbin = centerbin - self.halfwidth
        return [minbin]
    '''
    가장 기본적인 Encoder.
    제한된 작은 숫자를 인코딩
    ''' 
    def encode_vanilla(self, value):
        
        range_val = self.max_val - self.min_val   # 범위

        # 입력 데이터 제한
        # Cut lower and upper limits
        if(value > self.max_val):
            value = self.max_val
        elif(value < self.min_val):
            value = self.min_val
            
        bucketIdx = self._getFirstOnBit(value)[0]
        output = np.zeros(self.out_size)
        if bucketIdx is None:
          # None is returned for missing value
          output[0:self.n] = 0  #TODO: should all 1s, or random SDR be returned instead?
        else:
            # Possible problem here:
            output[:self.n] = 0
            minbin = bucketIdx
            maxbin = minbin + self.w
            if self.periodic:
                if maxbin >= self.n:
                    bottombins = maxbin - self.n + 1
                    output[:int(bottombins)] = 1
                    maxbin = self.n - 1
                if minbin < 0:
                    topbins = -minbin
                    output[self.n - int(topbins):self.n] = 1
                    minbin = 0
            print("minbin: {}".format(minbin))
            print("maxbin: {}".format(maxbin))
            assert minbin >= 0
            assert maxbin < self.n
            output[int(minbin):int(maxbin) + 1] = 1
            #= math.floor(self.num_bucket * (value - self.min_val) / range_val) #minbin
            #j = minbin + w #maxbin
            #if value < 10:
            #    print("{}| i: {} | ({} * ({} - {}) / {})".format(
            #        value,i,self.num_bucket, value, self.min_val, range_val
            #    ))

            #if(i + self.w >= self.out_size):
            #    i -= 1
            #output = np.zeros(self.out_size)
            #output[i : i+self.w] = 1

        return output
    
    def encode_log(self, value):
        
        range_val = self.log_max - self.min_val   # 범위

        # 입력 데이터 제한
        if(value > self.log_max):
            value = self.log_max
        elif(value < self.min_val):
            value = self.min_val

        i = math.floor(self.num_bucket * np.log10(value - self.min_val) / np.log10(range_val))

        encoded_data = np.zeros(self.out_size)
        encoded_data[i : i+self.w] = 1

        return encoded_data
    
    
    
    def encode_delta(self, value_prev, value_cur):
        delta = value_cur - value_prev
        range_val = self.delta_max - self.delta_min   # 범위

        # 입력 데이터 제한
        if(delta > self.delta_max):
            delta = self.delta_max
        elif(delta < self.delta_min):
            delta = self.delta_min

        i = math.floor(self.num_bucket * (delta - self.delta_min) / range_val)
        encoded_data = np.zeros(self.out_size)
        encoded_data[i : i+self.w] = 1
 
        return encoded_data



    '''
    random hash encode - 기본적으로 사용
    hashing 을 사용해 output data 를 넓게 분포시킨다.
    한정된 output size 일 경우 해상도를 높일 수 있다.
    2 중 hashing 쓰기
    '''
    def encode(self, value):
        
        range_val = self.max_val - self.min_val   # 범위

        # 입력 데이터 제한
        if(value > self.max_val):
            value = self.max_val
        elif(value < self.min_val):
            value = self.min_val

        i = math.floor(self.num_bucket * (value - self.min_val) / range_val)
        if(i + self.w >= self.out_size):
            i -= 1
        encoded_data = np.zeros(self.out_size)
        
        for n in range(i, i+self.w):
            # 2 중 해싱
            key = ((n*n) % (self.out_size) + (n*n) % (3)) % (self.out_size)
            
            # 충돌 처리
            while(encoded_data[key] == 1):
                key += 4
                if(key >= self.out_size):
                    key = 0
                    
            encoded_data[key] = 1
            
        return encoded_data
    

class CategoryEncoder:
    '''
    간단한 카테고리 encoder
    겹치지않게 만든다.
    '''
    def __init__(self, category, w=3):
        self.category = category
        self.category_count = len(category)
        self.active_bits = w
        self.total_bit = self.category_count * self.active_bits
        self.encoded_data = np.zeros(self.total_bit)
    
    def encode(self, item):
        if(item not in self.category):
            print('N/A')
            return None
        
        start_bit = self.category.index(item) + (self.active_bits - 1)*self.category.index(item)
        self.encoded_data[start_bit : start_bit+self.active_bits] = 1
        
        return self.encoded_data



class CycleEncoder:
    '''
    겹치게 만든다.
    case by case 로 hardcoding 이 필요함.
    '''
    def __init__(self, category, active_bits=3, resolution=5):
        self.category = category
        self.category_count = len(category)
        self.active_bits = active_bits
        self.resolution = resolution
        self.total_bit = self.category_count * self.resolution
        self.encoded_data = np.zeros(self.total_bit)
    
    def encode(self, time):
        #start_bit = 
        
        return self.encoded_data



class CategoryEncoder:
    '''
    간단한 카테고리 encoder
    겹치지않게 만든다.
    '''
    def __init__(self, category, active_bits=3):
        self.category = category
        self.category_count = len(category)
        self.active_bits = active_bits
        self.total_bit = self.category_count * self.active_bits
        self.encoded_data = np.zeros(self.total_bit)
    
    def encode(self, item):
        if(item not in self.category):
            print('N/A')
            return None
        
        start_bit = self.category.index(item) + (self.active_bits - 1)*self.category.index(item)
        self.encoded_data[start_bit : start_bit+self.active_bits] = 1
        
        return self.encoded_data



def WeekEncoder(day):
    '''
    주중과 주말을 category 화 하여 encoding.
    - SUN - MON - TUE - WED - THU - FRI - SAT -
    겹치지않게 만든다.
    '''
    data_size = 10
    
    if(day == 'SUN' or day == 'SAT'):
        start_bit = 0
    elif(day == 'MON' or day == 'TUE' or day == 'WED' or 
         day == 'THU' or day == 'FRI'):
        start_bit = int(data_size / 2)
    else:
        print("N/A")
        return 0
        
    encoded_data = np.zeros(data_size)
    encoded_data[start_bit : start_bit + int(data_size/2)] = 1
    
    return encoded_data

