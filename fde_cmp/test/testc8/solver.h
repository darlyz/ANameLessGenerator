/*******************************************************************************
 *
 *              constants for solver types
 *
 ******************************************************************************/
#define az_cg               0 /* preconditioned conjugate gradient method     */
#define az_gmres            1 /* preconditioned gmres method                  */
#define az_cgs              2 /* preconditioned cg squared method             */
#define az_tfqmr            3 /* preconditioned transpose-free qmr method     */
#define az_bicgstab         4 /* preconditioned stabilized bi-cg method       */
#define az_slu              5 /* super LU direct method.                      */
#define az_symmlq           6 /* indefinite symmetric like symmlq             */
#define az_gmresr           7 /* recursive GMRES (not supported)              */
#define az_fixed_pt         8 /* fixed point iteration                        */
#define az_analyze          9 /* fixed point iteration                        */
#define az_lu              10 /* sparse LU direct method. Also used for a     */
#define az_cg_condnum      11
#define az_gmres_condnum   12
#define superlu            13
/* preconditioning option.  NOTE: this should   */
/* be the last solver so that AZ_check_input()  */
/* works properly.                              */

/*******************************************************************************
 *
 *              constants for preconditioner types
 *
 ******************************************************************************/
#define az_none             0 /* no preconditioning. Note: also used for      */
/* scaling, output, overlap options options     */
#define az_jacobi           1 /* Jacobi preconditioning. Note: also used for  */
/* scaling options                              */
#define az_sym_gs           2 /* symmetric Gauss-Siedel preconditioning       */
#define az_neumann          3 /* Neumann series polynomial preconditioning    */
#define az_ls               4 /* least-squares polynomial preconditioning     */
#define az_ilu              6 /* domain decomp with  ilu in subdomains        */
#define az_bilu             7 /* domain decomp with block ilu in subdomains   */
#define az_icc              8 /* domain decomp with incomp Choleski in domains*/
#define az_ilut             9 /* domain decomp with ilut in subdomains        */
/* #define az_lu           10    domain decomp with   lu in subdomains        */
#define az_rilu            11 /* domain decomp with rilu in subdomains        */
#define az_recursive       12 /* Recursive call to AZ_iterate()               */
#define az_smoother        13 /* Recursive call to AZ_iterate()               */
#define az_dom_decomp      14 /* Domain decomposition using subdomain solver  */
/* given by options[AZ_subdomain_solve]         */
#define az_multilevel      15 /* Do multiplicative domain decomp with coarse  */
/* grid (not supported).                        */
#define az_user_precond    16 /*  user's preconditioning */
/* Begin Aztec 2.1 mheroux mod */
#define az_bilu_ifp        17 /* dom decomp with bilu using ifpack in subdom  */
/* End Aztec 2.1 mheroux mod */

/*******************************************************************************
 *
 *              constants for scaling types
 *
 ******************************************************************************/
/* #define az_none          0    no scaling                                   */
/* #define az_jacobi        1    Jacobi scaling                               */
#define az_bjacobi          2 /* block Jacobi scaling                         */
#define az_row_sum          3 /* point row-sum scaling                        */
#define az_sym_diag         4 /* symmetric diagonal scaling                   */
#define az_sym_row_sum      5 /* symmetric diagonal scaling                   */
#define az_equil            6 /* equilib scaling */
#define az_sym_bjacobi      7 /* symmetric block Jacobi scaling. NOTE: this   */
/* should be last so that AZ_check_input()      */
/* works properly.                              */

//short name
#define cg              az_cg
#define gmres           az_gmres
#define cgs             az_cgs
#define tfqmr           az_tfqmr
#define bicgstab        az_bicgstab
#define symmlq          az_symmlq
#define gmresr          az_gmresr
#define fixed_pt        az_fixed_pt
#define analyze         az_analyze
#define lu              az_lu
#define cg_condnum      az_cg_condnum
#define gmres_condnum   az_gmres_condnum
#define slu             superlu

#define none            az_none
#define jacobi          az_jacobi
#define sym_gs          az_sym_gs
#define neumann         az_neumann
#define ls              az_ls
#define ilu             az_ilu
#define bilu            az_bilu
#define icc             az_icc
#define ilut            az_ilut
#define rilu            az_rilu
#define recursive       az_recursive
#define smoother        az_smoother
#define dom_decomp      az_dom_decomp
#define multilevel      az_multilevel
#define user_precond    az_user_precond
#define bilu_ifp        az_bilu_ifp

#define bjacobi         az_bjacobi
#define row_sum         az_row_sum
#define sym_diag        az_sym_diag
#define sym_row_sum     az_sym_row_sum
#define equil           az_equil
#define sym_bjacobi     az_sym_bjacobi
//short name

enum {no, yes};
enum {dofact, samepattern, samepattern_samerowperm, factored};
enum {natural, mmd_ata, mmd_at_plus_a, colamd,
      metis_at_plus_a, parmetis, zoltan, my_permc
     };
enum {notrans, trans, conj};
enum {norefine, slu_single=1, slu_double, slu_extra};

struct solveroptions
{
    int solver,az_max_iter,az_precond,az_poly_ord,
        az_scaling,az_subdomain_solve;
    int slu_Fact,slu_Equil,slu_ColPerm,slu_Trans,slu_IterRefine,
        slu_SymmetricMode,slu_PivotGrowth,
        slu_ConditionNumber,slu_PrintStat;
    double slu_DiagPivotThresh,az_tol;
};
struct solveroptions solvoptions;
#define solvtag solvoptions.solver
#define default_solver bicgstab
#define default_solvpara ls
void setsolver(int solv,int solvp);
