#ifndef _K_UTILS_H
#define _K_UTILS_H

/**
 * interpolice
 */
long double interpolice(long double, long double* , long double*,int);

/**
 * C implemetation of WeightRandom PythonClass
 */
typedef struct weight_random_t weight_random_t;

struct weight_random_t {
	/**
	 * array of weights (length of 3600)
	 */
	long double * weights;

	/**
	 * spread function params 
	 */
	long double a,b,c,d,k;

	/**
	 * initial data
	 */
	long double x0,x1,y1,y2;

};

/**
 * Constructor
 * params:
 *   p0 = [ x0 , x1 , y1 , y2]
 *   p1 = [ a, b, c]
 *   p2 = [ d, k ]
 */
weight_random_t* weight_random_create(long double*,long double*,long double*);

/**
 * return random value according to weights
 */
int weight_random_rand(weight_random_t*,long double);

/**
 * predict how many objs will be in 24 hours
 * params: count_now - number of objects now
 *         now       - time in seconds since 00:00 at midnight
 */
int weight_random_will_be(weight_random_t*,int,int);

/**
 * destructure
 */
void weight_random_destruct(weight_random_t*);

#endif /* _K_UTILS_H */