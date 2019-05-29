#### Unknown Variable, 'Disp':
	u, v, w, 
#### Coupled Variable, 'Coef':
	un, vn, wn, 
#### Coordinate Type, 'Coor': 3dxyz
	x, y, z, 
#### Default Material, 'Mate':
| var|value|
|:---:|:---:|
|pe|1.0e10|
|pv|0.3|
|fx|0.0|
|fy|0.0|
|fz|0.0|
|rou|3000.0|
|alpha|0.6|
#### Element Type, 'shap':
	Type 1: c8, First Order Hexahedral Element
		Applicable to: u, v, w, 
#### Element Type, 'coef_shap':
	Type 1: c8, First Order Hexahedral Element
		Applicable to: un, vn, wn, 
#### Element Integration Type, g3:
	Gaussian integral grade 3
#### mass items (Second Order Time Derivative), 'mass':
	Lumped mass Matrix:
$$ \int_{\Omega} rou*\frac{\partial^2 u}{\partial t^2}\delta u + \int_{\Omega} rou*\frac{\partial^2 v}{\partial t^2}\delta v + \int_{\Omega} rou*\frac{\partial^2 w}{\partial t^2}\delta w $$
#### damp items (First Order Time Derivative), 'damp':
	Lumped damp Matrix:
$$ \int_{\Omega} rou*alpha*\frac{\partial u}{\partial t}\delta u + \int_{\Omega} rou*alpha*\frac{\partial v}{\partial t}\delta v + \int_{\Omega} rou*alpha*\frac{\partial w}{\partial t}\delta w $$
#### Stiffness items, 'stif'
	 Distribute Stiffness Matrix:
$$ \int_{\Omega} sm_{ij}*fact*ev_{i}\delta ev_{j}+ \int_{\Omega} shear*fact*ep_{i}\delta ep_{i}$$
